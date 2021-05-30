import matplotlib.pyplot as plt
from matplotlib import animation


class Visualizer:
    def __init__(self, shape: tuple, plots: list):
        '''
        - shape -- shape of matplotlib figure,
        - parameters of each plot:
        parameters = [
            (position, rowspan, colspan)
        ]. 
        Example:
        parameters = [
            ((0, 0), 2, 2),
            ((0, 2), 1, 1),
            ((1, 2), 1, 1)
        ]
        '''
        self.fig = plt.figure()
        self.axs = []

        for (pos, rowspan, colspan) in plots:
            self.axs.append(plt.subplot2grid(shape, pos, rowspan = rowspan, colspan = colspan))

    def set_axs_lims(self, lims: list) -> None:
        for i, (xleft_lim, xright_lim, ytop_lim, ybottom_lim) in enumerate(lims):
            self.axs[i].set_xlim(xleft_lim, xright_lim)
            self.axs[i].set_ylim(ytop_lim, ybottom_lim)

    def set_axs_labels(self, labels: list) -> None:
        for i, (xlabel, ylabel) in enumerate(labels):
            self.axs[i].set_xlabel(xlabel)
            self.axs[i].set_ylabel(ylabel)
            self.axs[i].yaxis.set_label_coords(0.08, 0.5)
            self.axs[i].xaxis.set_label_coords(0.5, 0.05)

    def set_data(self, data: list, titles: list) -> None:
        self.data = data
        self.titles = titles

    def animate(self, fps: int = 15, sep: int = 0, filename: str = '', dpi: int = 100, width: int = 1400, height: int = 800) -> None:
        '''
        - fps - number of frames per second.
        - sep - separator after which particles are drawn in another color.
        - filename - filename of output file. For no output file leave blank.
        - dpi - dots per inch
        - width - width in pixels
        - height - height in pixels
        '''
        lines1 = [ax.plot([], [], 'bo', ms = 72. / self.fig.dpi)[0] for ax in self.axs]
        lines2 = [ax.plot([], [], 'ro', ms = 72. / self.fig.dpi)[0] for ax in self.axs]

        def init():
            for line in lines1 + lines2:
                line.set_data([], [])

            return lines1, lines2

        def update_frame(frame):
            plt.suptitle(self.titles[frame])

            for i in range(len(lines1)):
                lines1[i].set_data(self.data[i][0][frame][:sep], self.data[i][1][frame][:sep])
                lines2[i].set_data(self.data[i][0][frame][sep:], self.data[i][1][frame][sep:])

            return lines1, lines2

        self.fig.set_size_inches(width / dpi, height / dpi)

        anim = animation.FuncAnimation(self.fig, update_frame, init_func=init, frames = len(self.data[0][0]), interval = 1 / fps * 1000, blit = False, save_count = len(self.data[0][0]))

        if filename != '':
            anim.save(filename, fps = fps, dpi = 100)

        plt.show()
