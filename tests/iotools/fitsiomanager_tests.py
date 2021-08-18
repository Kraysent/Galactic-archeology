from archeology.iotools import FITSReadManager, FITSWriteManager
import time
import numpy as np

class FITSIOTest:
    def profile_io(self):
        reader = FITSReadManager('data/models/flat_out1.fits')
        writer = FITSWriteManager('data/models/flat_test_out1.fits')
        
        print('read\twrite')
        while reader.next_frame():
            start = time.time()

            snapshot = reader.read_data()

            middle = time.time()

            writer.append_data(snapshot)

            end = time.time()
            print(f'{np.round(middle - start, 2)}\t{np.round(end - middle, 2)}')
    