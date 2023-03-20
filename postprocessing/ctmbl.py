# Script that takes/asks for a directory containing 1d ester models
# then plot the radius in terms of Solar Mass
# separating curves in terms of Z

import os, re, argparse, logging
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import ester

ARGS = None
LOGGER = None
# the list of attributes to extract from each model
ATTRIBUTES = ["M", "R", "Z", "Tc", "X", "ndomains", "eos", "Omega_bk", "test_virial", "test_energy"]
ARRAYS_ATTR = ["Z", "X"]

def plot_scatterplot2D(ax, stars):
    if len(stars) == 0:
        LOGGER.error("Nothing to display, stars' empty")
        exit(1)

    X = ARGS.plot[0]
    Y = ARGS.plot[1]
    C = ARGS.plot[2]

    norm=plt.Normalize(0,1)
    cmap = colors.LinearSegmentedColormap.from_list("my_rainbow", ["purple", "cyan", "blue", "green", "yellow", "red"], 256)

    ax.set_xlabel(X)
    ax.set_ylabel(Y)

    LOGGER.info("Display stars")

    return ax.scatter(stars[X], stars[Y], c=stars[C], data=stars, cmap=cmap, norm=norm)

# obsolete:
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
    X = ARGS.plot[0]
    Y = ARGS.plot[1]
    Z = ARGS.plot[2]

    ax.scatter(stars[X], stars[Y], stars[Z], marker='^')

    ax.set_xlabel(X)
    ax.set_zlabel(Z)
    ax.set_ylabel(Y)

def plot_it(stars):
    fig = plt.figure()
    if ARGS.scatterplot3D:
        ax = fig.add_subplot(projection='3d')
        plot_scatterplot3D(ax, stars)
    else:
        ax = fig.add_subplot()
        sc = plot_scatterplot2D(ax, stars)

        # test disaply has been deactivated: not updated since `stars` format update
        #ax = ax.twinx()
        #plot_tests_fM(ax, stars)

        cbar = fig.colorbar(sc, ax=ax, label=ARGS.plot[2])

    plt.show()

def yield_model(models_paths):

    for path in models_paths:
        is_model_2d = re.search("2d|w", path) is not None

        if ARGS.ester == 1:
            if is_model_2d:
                LOGGER.warning("Ignore %s, seems to be 2D model", path)
                continue
            else:
                model = ester.star1d(path)
        elif ARGS.ester == 2:
            if is_model_2d:
                model = ester.star2d(path)
            else:
                LOGGER.warning("Ignore %s, seems to be 1D model", path)
                continue
        else:
            logging.critical("Unknown ESTER model dimension: %s", ARGS.ester)
            exit(1)

        LOGGER.info("parsing model file at path '%s'", path)
        yield is_model_2d, model

def get_models_paths(folder):
    # list files in the chosen folder
    files = [os.path.join(folder, f) for f in os.listdir(folder)]
    # create a list of path (prepend folder to files) of h5 files (regexp)

    models_paths = []
    for f in files:
        if re.search(".h5$", f) is not None:
            models_paths.append(f)
        elif os.path.isdir(f) and ARGS.recursive:
            models_paths.extend(get_models_paths(f))

    return models_paths

def main():
    # get models paths
    models_paths = []
    for folder in ARGS.folders:
        models_paths.extend(get_models_paths(folder))
    LOGGER.debug("Found %s models: [%s]", len(models_paths), models_paths)

    stars = {}

    # stars initialization
    for attr in ATTRIBUTES:
        stars.update({attr: []})

    if len(models_paths) == 0:
        LOGGER.warning("No models found in this directory, using older values for stars dict")
        stars = {'M': [5.9673e+35, 5.9673e+35, 5.9673e+35, 5.9673e+35, 5.9673e+35, 5.9673e+35, 5.9673e+35, 5.9673e+35, 5.9673e+35, 5.9673e+35, 5.9673e+35, 5.9673e+35, 5.9673e+35, 5.9673e+35], 'R': [537657731047.3633, 538362543399.5326, 531023176242.3185, 528667956215.7965, 539041309219.3218, 542789112936.22253, 532686918944.3331, 531910984129.35675, 529017952555.08997, 535771357789.99286, 539773843550.49084, 533255814274.48834, 540945868383.56226, 530130137844.09235], 'Z': [1.9999999989472875e-09, 1.9999999989472875e-09, 1.9999999989472875e-09, 1.9999999989472875e-09, 1.9999999989472875e-09, 1.9999999989472875e-09, 1.9999999989472875e-09, 1.9999999989472875e-09, 1.9999999989472875e-09, 1.9999999989472875e-09, 1.9999999989472875e-09, 1.9999999989472875e-09, 1.9999999989472875e-09, 1.9999999989472875e-09], 'Omega_bk': [0.42, 0.44, 0.25, 0.0, 0.46, 0.54, 0.32, 0.29, 0.1, 0.38, 0.48, 0.34, 0.51, 0.2], 'test_virial': [-4.4069659033141306e-10, -6.846696543050257e-10, -2.543454336034756e-11, 2.947120325558217e-11, -8.155138786491989e-10, -2.5587931773429773e-10, -7.99460497802329e-11, 9.27606880196663e-11, -1.7458257062230587e-11, -1.0702017050334689e-10, -1.1687579792862834e-09, -2.017430666967357e-11, -1.0131129268842187e-09, -3.541145154883907e-11], 'test_energy': [4.540967454914486e-06, 1.4889536484881958e-05, 1.0650544735957296e-06, 8.519671804101867e-08, -4.002785322500465e-05, 0.00038627494832817226, 3.587649685558525e-06, -2.3694929111380636e-06, 5.482976060145386e-07, 1.4061019751383358e-06, 5.053838745262048e-05, -4.613880845037216e-06, 0.0003312559829097926, 1.858352061792795e-06]}

    # stars filling
    for is_model_2d, model in yield_model(models_paths):
        # TEMPLATE: {"M": [model.M], "R": [model.R], "Z": [model.Z], Omega_bk": [model.Omega_bk], "test_virial": [model.test_virial], "test_energy": [model.test_energy]}
        for attr in ATTRIBUTES:
            if attr in ARRAYS_ATTR:
                stars[attr].append(getattr(model, attr)[0][0])
                continue
            stars[attr].append(getattr(model, attr))
        LOGGER.debug("new values 'M: %s, R:%s, Z:%s, Omega_bk:%s' added", float(model.M), float(model.R), float(model.Z[0][0]), float(model.Omega_bk))

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
        "--folders",
        "-f",
        default=".",
        help="the path to the folder containing 1d models",
        nargs="+",
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
        "--scatterplot3d",
        "-3",
        dest="scatterplot3D",
        action="store_true",
        help="plot a 3D scatter plot of R, M and log(Z) instead of R=f(M,Z) 2D curves"
    )
    parser.add_argument(
        "--ester",
        "-e",
        type=int,
        choices=[1,2],
        default=1,
        dest="ester",
        help="dimension of the model to plot (1D or 2D), default to 1"
    )
    parser.add_argument(
        "--plot",
        default=["M","R","Omega_bk"],
        type=lambda s: s.split(','),
        help=f"which parameter to plot in {ATTRIBUTES}, comma separated, between 2 and 3"
    )
    parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        help="if used, look recursively in the folders to find models"
    )

    # Global variables
    ARGS = parser.parse_args()
    LOGGER = logging.getLogger("app")

    # Validation
    if ARGS is None:
        logging.critical("Arg parsing failed, exiting...")
        exit(1)
    elif LOGGER is None:
        logging.critical("Logger setup failed, exiting...")
        exit(1)

    for folder in ARGS.folders:
        if not os.path.exists(folder) or os.path.isfile(folder):
            logging.critical("'%s' isn't a path to a folder", ARGS.folders)
            exit(1)
    if len(ARGS.plot) != 3:
        logging.critical("Exactly 3 attributes are needed with --plot, got %s: %s", len(ARGS.plot), ARGS.plot)
        exit(1)
    for attr in ARGS.plot:
        if attr not in ATTRIBUTES:
            logging.critical("'%s' is an unknown attributes, please choose only one of %s", attr, ATTRIBUTES)
            exit(1)
    logging.info("Will look for %dD ESTER models", ARGS.ester)

    # LOGGER setup
    level = (5 - ARGS.verbose)*10
    LOGGER.setLevel(level)

    try:
        main()
    except KeyboardInterrupt:
        logging.error("Detected CTRL+C, exiting...")