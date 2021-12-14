// -*- C++ -*-                                                                  
////////////////////////////////////////////////////////////////////////////////
///                                                                             
/// \file   inc/forces.h                                                        
///                                                                             
/// \brief  contains declarations of class falcON::forces, which serves as      
///	    joint interface for any force computation in falcON.                
///                                                                             
/// \author Walter Dehnen                                                       
/// \date   1999-2010                                                           
///                                                                             
////////////////////////////////////////////////////////////////////////////////
//                                                                              
// Copyright (C) 1999-2010 Walter Dehnen                                        
//                                                                              
// This program is free software; you can redistribute it and/or modify         
// it under the terms of the GNU General Public License as published by         
// the Free Software Foundation; either version 2 of the License, or (at        
// your option) any later version.                                              
//                                                                              
// This program is distributed in the hope that it will be useful, but          
// WITHOUT ANY WARRANTY; without even the implied warranty of                   
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU            
// General Public License for more details.                                     
//                                                                              
// You should have received a copy of the GNU General Public License            
// along with this program; if not, write to the Free Software                  
// Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.                    
//                                                                              
////////////////////////////////////////////////////////////////////////////////
#ifndef falcON_included_forces_h
#define falcON_included_forces_h 1
#ifndef falcON_included_types_h
#  include <public/types.h>
#endif
#ifndef falcON_included_default_h
#  include <public/default.h>
#endif
#ifndef falcON_included_body_h
#  include <body.h>
#endif
////////////////////////////////////////////////////////////////////////////////
namespace falcON {
  class OctTree;
  class GravMAC;
  class GravStats;
  class GravEstimator;
  class PartnerEstimator;
  class SphEstimator;
  class EquationOfState;
  class ArtificialViscosity;
  // ///////////////////////////////////////////////////////////////////////////
  // ///////////////////////////////////////////////////////////////////////////
  //                                                                            
  //  class falcON::forces                                                      
  //                                                                            
  /// serves as joint interface for any force computation in falcON             
  ///                                                                           
  /// Force computation in falcON is done using estimators, for example         
  /// GravEstimator of file gravity.h for gravitational forces. In order to     
  /// provide a simplified interface to the force computation, class forces     
  /// takes care of GravEstimator etc and can be used as a base class for an    
  /// N-body code or its force engine, which is actually done in file nbody.h.  
  ///                                                                           
  /// Known bugs and problems\n                                                 
  /// 1 Test-bodies are not possible\n                                          
  /// A body that is loaded into the tree but has zero mass, will get NaN (not a
  /// number) as acceleration (or a floating point exception is thrown). This is
  /// because the code computes first the force = mass times acceleration (it is
  /// symmetric and hence better suited for the computation of mutual           
  /// interactions) and then divides by the mass to obtain the acceleration. The
  /// only possible work-around this problem is to set the mass of potential    
  /// test bodies much smaller than the masses of source bodies. However, this  
  /// must be done such that the gravity of test bodies is everywhere neglible  
  /// compared to that of the source bodies.  Note, however, that this          
  /// work-around is wasteful: it computes the forces generated by the test     
  /// bodies. (You have been warned!)                                           
  ///                                                                           
  /// 2 Bodies at identical positions\n                                         
  /// The code cannot cope with more than Ncrit bodies at the same position     
  /// (within the floating point accuracy). This situation will lead to an      
  /// infinitely deep tree, i.e. the maximum allowed tree depth will be exceeded
  /// and the code aborts with an error message.                                
  ///                                                                           
  /// REFERENCES                                                              \n
  /// Dehnen W., 2000, ApJ, 536, L39                                          \n
  /// Dehnen W., 2001, MNRAS, 324, 273                                        \n
  /// Dehnen W., 2002, J. Comp. Phys., 179, 27                                \n
  // ///////////////////////////////////////////////////////////////////////////
  // ///////////////////////////////////////////////////////////////////////////

  class forces {

  public:
    //==========================================================================
    /// \name construction and re-setting of parameters                         
    //@{                                                                        
    //--------------------------------------------------------------------------
    /// standard ctor for usage in falcON and other C++ code                    
    ///                                                                         
    /// Once an object of type forces has been create, one cannot change the    
    /// set of bodies used, but of course, one can change the data and number   
    /// of bodies stored in this set (see class bodies). Only the first two     
    /// arguments are obligatory.                                               
    /// \param B   pter to set of bodies for which forces etc shall be computed 
#ifdef falcON_ADAP
    /// \param eps   global or maximal gravitational softening length 
#else
    /// \param eps   gravitational softening length; ignored if individual eps_i 
#endif
    /// \param th    gravitational opening angle theta 
    /// \param ker   type of gravitational softening kernel 
    /// \param in    use individual softening lengths eps_i?
    /// \param G     Newton's gravitational constant
    /// \param mt    type of multipole acceptance criterion (MAC_type) 
    /// \param epssk global softening length for sink particles
    /// \param fsink theta reduction factor for sink particles
    /// \param dir   constants controlling usage of direct summation for gravity 
#ifdef falcON_SPH
    /// \param sdr   constants controlling cell-opening for SPH force computation
#endif
    forces (const bodies  *B,
	    real           eps,
	    real           th     = Default::theta,
	    kern_type      kt     = Default::kernel,
	    bool           in     = false,
	    real           G      = one,
	    MAC_type       mt     = theta_of_M,
	    real           epssk  = zero,
	    real           fsink  = one,
	    const unsigned dir[4] = Default::direct
#ifdef falcON_SPH
	   ,const unsigned sdr[3] =Default::SPHdirect
#endif
	    ) falcON_THROWING;
    //--------------------------------------------------------------------------
    /// reset the gravitational softening parameters                            
    /// \param eps   gravitational softening length
    /// \param epssk softening length for sink particles 0: same as @a eps
    /// \param ker   type of gravitational softening kernel
    void reset_softening(real      eps,
			 real      epssk=zero,
			 kern_type ker=Default::kernel) const;
    //--------------------------------------------------------------------------
    /// reset the gravitational force approximation parameters                  
    /// \param th  gravitational opening angle theta                            
    /// \param mt  type of multipole acceptance criterion (MAC_type)            
    void reset_opening(real        th,
		       MAC_type    mt=Default::mac) const;
    //--------------------------------------------------------------------------
    /// reset Newton's gravitational constant                                   
    /// \param G new value for  Newton's gravitational constant                 
    void reset_NewtonsG(real G) const;
    //@}
    //==========================================================================
    /// dtor: will delete all allocated structures (tree & estimators)          
    ~forces();
    //==========================================================================
    /// \name generation and maintainance of an oct tree                        
    //@{                                                                        
    //--------------------------------------------------------------------------
    /// grows a new oct tree structure from scratch                             
    ///                                                                         
    /// Cells containing \a Ncrit of less bodies will \b not be splitted.       
    /// Experiments showed that for a full force calculation Ncrit=6-8 results  
    /// in an optimal balance between tree building and force gravitational     
    /// force approximation, where as Ncrit=1 requires a few % more CPU time and
    /// 20% more memory.\n                                                      
    /// If called repeatedly, the previous tree structure will be used to help  
    /// the construction of the new tree, which results in a speed-up of about  
    /// a factor 2 compared to the first ever tree build.                       
    /// \param Ncrit maximum number of bodies per final tree cell (= leaf cell) 
    /// \param croot optional root-centre                                       
    void grow(int         Ncrit =Default::Ncrit,
	      const vect* croot =0) falcON_THROWING;
    //--------------------------------------------------------------------------
    /// re-use an old tree structure                                            
    ///                                                                         
    /// We maintain the tree as a linked structure of nodes, but acknowledge    
    /// that bodies may have moved out of their boxes. In order to do so, the   
    /// radius around each cell ("size") containing all bodies is re-computed.  
    /// Clearly, if the bodies have moved a lot, the sizes of the cells will be 
    /// much larger than the physical size of the associated boxes, and the     
    /// tree traversal will be very inefficient.\n                              
    /// However, if the bodies have moved only little, the force computation is 
    /// hardly slowed down and re-using an old tree saves the costs for         
    /// establishing a new one.\n                                               
    /// Clearly, if the number of bodies has changed since the last grow(),     
    /// this will \b not be reflected in the tree by using reuse().             
    void reuse() falcON_THROWING;
    //@}
    //==========================================================================
    /// \name computation of gravitational forces                               
    //@{                                                                        
    //--------------------------------------------------------------------------
    /// approximate the gravitational forces using the falcON algorithm         
    ///                                                                         
    /// This routine provides a convenient interface to the falcON force        
    /// algorithm with the three steps:\n                                       
    /// - computes the cell's source properties (upward pass),                  
    /// - performs all interactions (interaction phase), and                    
    /// - evaluates the gravity for active bodies (evaluation phase).           
#ifdef falcON_ADAP
    /// For individual adaptive softening the routine can do more for you before
    /// the forces are actually computed:\n                                     
    /// If \a Nsoft is non-zero, it estimates for each active body the local    
    /// number density (using the number density of the smallest cell containing
    /// that particle and not less than \a Nref bodies).                        
    /// If \a efac is zero, the bodies softening lengths are set such that,     
    /// based on the estimated number density, their eps-spheres contain Nsoft  
    /// bodies, but eps_i <= parameter set at construction or reset_softening().
    /// If \a efac is non zero, Eps is computed in the same way, and the        
    /// new softening is set to\n                                               
    ///        eps_new = Eps^2 / eps_old,\n                                     
    /// with the restriction  eps_new in [eps_old/efac, eps_old*fac].\n         
    /// If eps_i is adjusted in this way, it will be copied back to the bodies. 
#endif
    /// \note                                                                   
    /// Since Oct-2003, you MUST not change the bodies activity flag between    
    /// tree growth (or re-growth, re-use) and a call to                        
    /// approximate_gravity(). Whenever you change the flags, you MUST either   
    /// first (re-)grow the tree before you can approximate_gravity() or update 
    /// the flags (of the tree leafs and cells) yourself (if you know how to do 
    /// that, that is).                                                         
    ///                                                                         
    /// \note                                                                   
    /// Bodies not loaded into tree at grow() will neither receive gravity nor  
    /// will their masses matter. Note that by default sink bodies are NOT      
    /// loaded into the tree
    ///
    /// \note
    /// Since Mar-2010, the option not to combine the interaction and evluation
    /// phase (used to be the first argument) is no longer possible.
    ///                                                                         
    /// \param all compute forces for all or only active bodies?                
#ifdef falcON_ADAP
    /// \param Nsoft # bodies within individual adaptive softening volumes      
    /// \param Nref  # bodies used in adjusting eps_i                           
    /// \param emin  minimum eps_i                                              
    /// \param efac  maximum change factor for eps_i                            
#endif
    void approximate_gravity(bool     all   = false
#ifdef falcON_ADAP
			    ,real     Nsoft = zero,
			     unsigned Nref  = 0u,
			     real     emin  = zero,
			     real     efac  = zero
#endif
			     ) falcON_THROWING;
    //--------------------------------------------------------------------------
    /// direct-summation computation of the gravitational forces                
    ///                                                                         
    /// This routines has been provided for test purposes. The meaning of the   
    /// parameters are identical to those of approximate_gravity() above.       
    void exact_gravity(bool     all   =false
#ifdef falcON_ADAP
		      ,real     Nsoft =zero,
		       unsigned Nref  =0u,
		       real     emin  =zero,
		       real     efac  =zero
#endif
		       ) falcON_THROWING;
    //@}
    //==========================================================================
    /// \name crude density estimations                                         
    //@{                                                                        
    //--------------------------------------------------------------------------
    /// crude estimation of the mass volume density                             
    ///                                                                         
    /// Sets the bodies density to be the mean density of the smallest cell     
    /// containing the body and at least \a Nx in total.                        
    /// \note                                                                   
    /// When using test bodies (bodies with zero or tiny mass), this guess for  
    /// the mass density can have terrible errors. Moreover, when the tree has  
    /// not been grow()n but simply reuse()ed, these estimate will not change.  
    /// \param Nx  minimum # bodies in cells used to estimate density           
    /// \param all estimate density for all or only active bodies?              
    void estimate_rho(unsigned Nx, bool all = 0) falcON_THROWING;
    //--------------------------------------------------------------------------
    /// crude estimation of the mass surface density                            
    ///                                                                         
    /// Sets the bodies density to be the mean surface density of the smallest  
    /// cell containing the body and at least \a Nx in total.                   
    /// \note                                                                   
    /// When using test bodies (bodies with zero or tiny mass), this guess for  
    /// the mass density can have terrible errors. Moreover, when the tree has  
    /// not been grow()n but simply reuse()ed, these estimate will not change.  
    /// \param Nx  minimum # bodies in cells used to estimate density           
    /// \param all estimate density for all or only active bodies?              
    void estimate_sd(unsigned Nx, bool all = 0) falcON_THROWING;
    //--------------------------------------------------------------------------
    /// crude estimation of the number volume density                           
    ///                                                                         
    /// Sets the bodies density to be the mean number density of the smallest   
    /// cell containing the body and at least \a Nx in total.                   
    /// \note                                                                   
    /// When the tree has not been grow()n but simply reuse()ed, these estimate 
    /// will not change.  \param Nx minimum # bodies in cells used to estimate  
    /// density \param all estimate density for all or only active bodies?      
    void estimate_n(unsigned Nx, bool all = 0) falcON_THROWING;
    //@}
    //==========================================================================
    // \name search for and counting of collision partners                      
    //{@                                                                        
    //--------------------------------------------------------------------------
    typedef bodies::index indx_pair[2];               ///< pair of bodies::index
    //--------------------------------------------------------------------------
    /// create a list of body pairs which interact                              
    ///                                                                         
    /// This routine can be used to find interaction partners for SPH or sticky 
    /// particle type interactions.\n                                           
    /// 1. sticky-particle type interactions\n                                  
    /// For this, \a tau >= 0. In this case, the routine makes a list of all    
    /// pairs {i,j} of indices i,j < Nsph for which\n                           
    /// - both flags indicate sticky particles \n                               
    /// - at least one is flagged being active \n                               
    /// - | (x_i+t*v_i) - (x_j+t*v_j) | < size_i + size_j  with t in [0,\a tau] 
    /// \n 2. SPH interations\n                                                 
    /// For this, \a tau < 0. In this case, the routines creates a list of all  
    /// pairs {i,j} of indices i,j < Nsph for which\n                           
    /// - both flags indicate SPH particles \n                                  
    /// - at least one is flagged being active \n                               
    /// - | x_i - x_j | < max(size_i,size_j)     IF \a Max==true\n              
    ///   OR | x_i - x_j | < size_i + size_j     IF \a Max==false\n             
    ///                                                                         
    /// In either case, if \a \count == true, we also count the interaction     
    /// partners for active bodies and write into to corresponding data field.  
    /// If \a list==0, but \a count == true, we only count partners.            
    ///                                                                         
    /// See file src/public/exe/TestPair.cc for an example application for both 
    /// supports.                                                               
    /// \param list  array of body pairs (must be pre-allocated by user)        
    /// \param nl    physical size of list (# elements allocated)               
    /// \param np    actual number of pairs found (and copied into list)        
    /// \param Max   use maximum of sum of sizes                                
    /// \param tau   time step for sticky-particle support                      
    /// \param count if true, the # partners is counted for each active body    
    void make_iaction_list(indx_pair*list,
			   unsigned  nl,
			   unsigned &np,
			   bool      Max,
			   real      tau,
			   bool      count) falcON_THROWING;
    //--------------------------------------------------------------------------
    /// just cound SPH interaction partners (see make_iaction_list())           
    /// \param Max   use maximum of sum of sizes                                
    void count_sph_partners(bool Max) falcON_THROWING;
    //@}                                                                        
    //==========================================================================
    // \name other features                                                     
    //{@                                                                        
    //--------------------------------------------------------------------------
    /// \return # bodies used in falcON
    unsigned No_bodies_used() const;
    /// \return # cells in the tree
    unsigned No_cells_used() const;
    /// \return # sets of Taylor series coefficients
    unsigned const&No_coeffs_used() const;
    /// dumps (almost) all info of the bodies and cells to files (ascii)
    /// \param cells file to dump cell data to
    /// \param leafs file to dump body data to
    void dump_nodes(const char*cells= 0,
		    const char*leafs= 0) const falcON_THROWING;
    /// write some statistics to given output stream
    void stats(std::ostream&) const;
    /// \return currently used MAC (multipole acceptance criterion)
    const MAC_type& MAC() const;
    /// \return a human-readable description of the currently used MAC
    const char* describe_MAC() const;
    /// \return are we currently using individual softening lengths?
    const bool& use_individual_eps() const;
    /// \return the currently used softening kernel
    const kern_type& kernel() const;
    /// \return a human-readable description of the currently used kernel
    const char* describe_kernel() const;
    /// \return the currently used (global) softening length
    const real& softening_length() const;
    /// \return the currently used (global) softening length
    const real& eps() const;
    /// \return the current value of Newton's G
    const real& NewtonsG() const;
    //--------------------------------------------------------------------------
    unsigned BB_interactions() const;    ///< return # body-body interactions
    unsigned MB_interactions() const;    ///< return # many-body interactions
    unsigned CB_interactions() const;    ///< return # cell-body interactions
    unsigned CC_interactions() const;    ///< return # cell-cell interactions
    unsigned total_interactions() const; ///< return # all interactions
    //--------------------------------------------------------------------------
    /// return tree
    const OctTree *tree       () const { return TREE; }
    /// return bodies
    const bodies*      const&Bodies     () const { return BODIES; }
    vect               const&root_center() const;  ///< return center of root
    real               const&root_radius() const;  ///< return radius of root
    unsigned           const&root_number() const;  ///< return # bodies in root
    real               const&root_mass  () const;  ///< return mass of root
    unsigned           const&root_depth () const;  ///< return depth of root
    const SphEstimator*const&Sph        () const { return SPHT; }
    //@}                                                                        
    //==========================================================================
  protected:
    unsigned No_bodies        () const { return BODIES->N_bodies(); }
    OctTree* const& my_tree   () const { return TREE; }
  private:
    forces                    ();
    forces                    (const forces&);
    forces& operator=         (const forces&);
    //--------------------------------------------------------------------------
    mutable GravStats     *STATS;
    const   bodies        *BODIES;
    int                    Ncrit;
    OctTree               *TREE;
    GravMAC               *GMAC;
    GravEstimator         *GRAV;
    PartnerEstimator      *PAES;
    const SphEstimator    *SPHT;
  };// class forces
  //////////////////////////////////////////////////////////////////////////////
} // namespace falcON
////////////////////////////////////////////////////////////////////////////////
#include <public/forces.cc>
#endif // falcON_included_forces_h