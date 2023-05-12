from matplotlib import pyplot as plt
from nudging import nudge_estimators
from preprocessing import generate_label_points

import sys
import os
from datetime import datetime
from math import floor

from geometry.diagram import Diagram


class VoronoiApproximation:

    def __init__(self, diagram:Diagram, omega:float, phi:float, gui:bool=False):
        self.diagram = diagram
        self.omega = omega
        self.phi = phi

        self.gui = gui
        
        self.done = False
        self.label_points, self.estimator_points = generate_label_points(diagram, omega)


    def on_press(self, event):
        print(event.key)
        sys.stdout.flush()
        if event.key == 'x':
            self.done = True


    def do_thingy(self, margin=1):
        iterations = 0
        self.points_satisfied = []
        begin = datetime.now()

        plt.gcf().canvas.mpl_connect('key_press_event', self.on_press)

        original_phi = self.phi

        self.done = False
        while(not self.done):
            nudged = nudge_estimators(self.estimator_points, self.label_points, self.phi, pull=True, push=True)
            iterations += 1

            if not nudged:
                plt.title(label="All label points satisfied!")
                self.done = True

            if self.gui:
                for p in self.estimator_points:
                    p.update_plot()

                    if self.diagram.point_inside_region(p, p.label):
                        p.plot_element[0].set_markerfacecolor('b')
                    else:
                        p.plot_element[0].set_markerfacecolor('aqua')


            satisfied_count = 0
            for l in self.label_points:
                if l.satisfied:
                    satisfied_count += 1

            satisfied_percentage = satisfied_count/len(self.label_points)

            self.phi = original_phi * (1-satisfied_percentage)

            if satisfied_percentage >= margin:
                self.done = True

            self.points_satisfied.append(satisfied_percentage)

            percent_bar_length = os.get_terminal_size().columns

            m = floor(satisfied_percentage * percent_bar_length)

            percent_bar = m * "█" + (percent_bar_length - m) * "░"

            progress = f"{percent_bar}"

            sys.stdout.write("\r" + progress)
            sys.stdout.flush()

            if self.gui:
                plt.pause(1e-10)

        end = datetime.now()

        sys.stdout.write("\r" + f"Finished in {end - begin} ({iterations} iterations)")
        sys.stdout.flush()
        print()

        return self.estimator_points