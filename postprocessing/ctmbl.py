# Script that takes/asks for a directory containing 1d ester models
# then plot the radius in terms of Solar Mass
# separating curves in terms of Z

import os, re, argparse, logging
import matplotlib.pyplot as plt
import numpy as np
import ester

ARGS = None
LOGGER = None

def plot_R_fM(stars, ax):
    if len(stars) == 0:
        LOGGER.error("Nothing to display, stars' empty")
        exit(1)

    color = "red"
    STYLES = iter(["+", "x"])

    ax.tick_params(axis='y', labelcolor=color)
    ax.set_xlabel("M/M_sun")
    ax.set_ylabel("R/R_sun")

    for key, value in stars.items():
        try:
            if len(stars[key]) == 0:
                LOGGER.error("Can't display stars[%s], empty", key)
                exit(1)
            ax.plot("M", "R", next(STYLES), data=stars[key], label=f"{key} Radius", color=color)
            LOGGER.info("Display stars[%s]", key)

        except StopIteration:
            LOGGER.error("Not enough STYLES to plot each set of datas, stopped at key '%s'", key)
            break

    ax.legend(loc='best')

def plot_tests_fM(stars, ax):
    color = "green"
    STYLES = iter(["+", "x"])
    
    ax.tick_params(axis='y', labelcolor=color)
    ax.set_ylabel("|test_virial|")
    ax.set_yscale("log")

    for key, value in stars.items():
        try:
            LOGGER.debug("plotting test_virial=f(M,Z=%s) : \nM: %s\ntest_virial: %s", key, stars[key]["M"], stars[key]["test_virial"])
            ax.plot("M", "test_virial", next(STYLES), data=stars[key], label=f"{key} test_virial", color=color)
            #ax.plot("M", "test_energy", next(STYLES), data=stars[key], label=key, color=color)
        except StopIteration:
            LOGGER.error("Not enough STYLES to plot each set of tests, stopped at key '%s'", key)
            break

    ax.legend(loc='upper right')

def plot_scatterplot3D(ax, stars):
    ax.scatter(stars['M'], stars['Z'], stars['Omega_bk'], marker='^')

    ax.set_xlabel('M/M_SUN')
    ax.set_zlabel('Omega_bk')
    ax.set_ylabel('log(Z)')

def plot_it(stars):
    fig = plt.figure()
    if ARGS.scatterplot:
        ax = fig.add_subplot(projection='3d')
        plot_scatterplot3D(ax, stars)
    else:
        ax = fig.add_subplot()
        plot_R_fM(stars, ax)
        ax = ax.twinx()
        plot_tests_fM(stars, ax)

    plt.show()

def main():
    # list files in the chosen folder
    files = os.listdir(ARGS.folder)
    # create a list of path (prepend ARGS.folder to files) of h5 files (regexp)
    models_paths = [os.path.join(ARGS.folder, f) for f in files if re.search(".h5$", f) is not None]
    LOGGER.debug("Found %s models: [%s]", len(models_paths), models_paths)

    stars = {}

    if len(models_paths) == 0:
        LOGGER.warning("No models found in this directory, using older values for M, R and Z lists")
        stars = {'1.9999999989472875e-09': {'M': [5.9673e+35, 5.9673e+35, 5.9673e+35, 5.9673e+35, 5.9673e+35, 5.9673e+35, 5.9673e+35, 5.9673e+35, 5.9673e+35, 5.9673e+35, 5.9673e+35, 5.9673e+35, 5.9673e+35, 5.9673e+35], 'R': [537657731047.3633, 538362543399.5326, 531023176242.3185, 528667956215.7965, 539041309219.3218, 542789112936.22253, 532686918944.3331, 531910984129.35675, 529017952555.08997, 535771357789.99286, 539773843550.49084, 533255814274.48834, 540945868383.56226, 530130137844.09235], 'Omega_bk': [0.42, 0.44, 0.25, 0.0, 0.46, 0.54, 0.32, 0.29, 0.1, 0.38, 0.48, 0.34, 0.51, 0.2], 'test_virial': [-4.4069659033141306e-10, -6.846696543050257e-10, -2.543454336034756e-11, 2.947120325558217e-11, -8.155138786491989e-10, -2.5587931773429773e-10, -7.99460497802329e-11, 9.27606880196663e-11, -1.7458257062230587e-11, -1.0702017050334689e-10, -1.1687579792862834e-09, -2.017430666967357e-11, -1.0131129268842187e-09, -3.541145154883907e-11], 'test_energy': [4.540967454914486e-06, 1.4889536484881958e-05, 1.0650544735957296e-06, 8.519671804101867e-08, -4.002785322500465e-05, 0.00038627494832817226, 3.587649685558525e-06, -2.3694929111380636e-06, 5.482976060145386e-07, 1.4061019751383358e-06, 5.053838745262048e-05, -4.613880845037216e-06, 0.0003312559829097926, 1.858352061792795e-06]}}
        M = [300.0, 300.0, 300.0, 300.0, 300.0, 300.0, 300.0, 300.0, 300.0, 300.0, 300.0, 300.0, 300.0, 300.0]
        R = [7.730432015841131, 7.740565793629011, 7.635040520631229, 7.6011772145797964, 7.750325074899523, 7.804210921171611, 7.658961779653622, 7.647805404529592, 7.606209454888944, 7.703309779182883, 7.760857438742486, 7.667141345239571, 7.777708788160053, 7.622200432548473]
        Z = [-8.698970004564613, -8.698970004564613, -8.698970004564613, -8.698970004564613, -8.698970004564613, -8.698970004564613, -8.698970004564613, -8.698970004564613, -8.698970004564613, -8.698970004564613, -8.698970004564613, -8.698970004564613, -8.698970004564613, -8.698970004564613]
        Omega_bk = [0.42, 0.44, 0.25, 0.0, 0.46, 0.54, 0.32, 0.29, 0.1, 0.38, 0.48, 0.34, 0.51, 0.2]
        LOGGER.info("These are 2d/m300/1st_gen values")

    # the list of attributes to extract from each model
    attributes = ["M", "R", "Z", "Omega_bk", "test_virial", "test_energy"]

    # stars initialization
    for attr in attributes:
        stars.update({attr: []})

    # stars filling
    for path in models_paths:
        model_2d = re.search("2d|w", path) is not None
        if model_2d:
            if ARGS.print_2d_stars:
                model = ester.star2d(path)
            else:
                LOGGER.warning("Ignore %s, seems to be 2D model", path)
                continue
        else:
            if ARGS.print_2d_stars:
                LOGGER.warning("Ignore %s, seems to be 1D model", path)
                continue
            else:
                model = ester.star1d(path)
        LOGGER.debug("parsing model file at path '%s'", path)

        # TEMPLATE: {"M": [model.M], "R": [model.R], "Z": [model.Z], Omega_bk": [model.Omega_bk], "test_virial": [model.test_virial], "test_energy": [model.test_energy]}
        for attr in attributes:
            stars[attr].append(getattr(model, attr))
        LOGGER.debug("new values 'M: %s, R:%s' added to stars dict at key '%s'", float(model.M), float(model.R), key)

    if ARGS.print:
        print("stars:", stars)

    # Normalize values on sun parameters
    # Pass test_* to absolute values (to be displayed on log scale)
    stars['M'] = list(map(lambda x: x/ester.M_SUN, stars['M']))
    stars['R'] = list(map(lambda x: x/ester.R_SUN, stars['R']))
    stars['test_virial'] = list(map(lambda x: abs(x), stars['test_virial']))
    stars['test_energy'] = list(map(lambda x: abs(x), stars['test_energy']))

    plot_it(stars)

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s [%(levelname)s]: %(message)s", level=logging.INFO)
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--folder",
        "-f",
        default=".",
        help="the path to the folder containing 1d models",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        type=int,
        choices=[0,1,2,3,4],
        default=3,
        help="the verbosity from 0 (quiet) to 4 (debug logs), default to 3"
    )
    parser.add_argument(
        "--print",
        "-p",
        action="store_true",
        help="if used, print to stdout the stars dict and M, R and Z lists, ignores verbosity"
    )
    parser.add_argument(
        "--3d",
        "-3",
        dest="scatterplot",
        action="store_true",
        help="plot a 3D scatter plot of R, M and log(Z) instead of R=f(M,Z) 2D curves"
    )
    parser.add_argument(
        "--2d",
        "-2",
        dest="print_2d_stars",
        action="store_true",
        help="look for 2D model stars instead of 1D models"
    )

    ARGS = parser.parse_args()
    LOGGER = logging.getLogger("app")

    if ARGS is None:
        logging.critical("Arg parsing failed, exiting...")
        exit(1)
    elif LOGGER is None:
        logging.critical("Logger setup failed, exiting...")
        exit(1)

    if not os.path.exists(ARGS.folder) or os.path.isfile(ARGS.folder):
        logging.warning("'%s' isn't a directory path, use working directory")

    level = (5 - ARGS.verbose)*10
    LOGGER.setLevel(level)

    try:
        main()
    except KeyboardInterrupt:
        logging.error("Detected CTRL+C, exiting...")