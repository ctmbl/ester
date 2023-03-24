# Script that takes/asks for a directory containing 1d ester models
# then plot the radius in terms of Solar Mass
# separating curves in terms of Z

import os, re, argparse, logging, pickle
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import ester

ARGS = None
LOGGER = None
SAVE_FILE = 'save_stars_data.pkl'
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

def filter_it(stars):
    if ARGS.filter is None:
        return

    parameter = ARGS.filter[0]
    value = ARGS.filter[1]

    def delete_at_index(i):
        for attr in ATTRIBUTES:
            stars[attr].pop(i)

    for i in range(len(stars[parameter])-1, -1, -1):
        if str(stars[parameter][i]) == value:
            delete_at_index(i)

def plot_it(stars):
    fig = plt.figure()

    filter_it(stars)

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

def get_default():
    with open(SAVE_FILE, 'rb') as f:
        stars = pickle.load(f)
    return stars

def save_default(stars):
    with open(SAVE_FILE, 'wb') as f:
        pickle.dump(stars, f)

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
        stars = get_default()

    # stars filling
    for is_model_2d, model in yield_model(models_paths):
        # TEMPLATE: {"M": [model.M], "R": [model.R], "Z": [model.Z], Omega_bk": [model.Omega_bk], "test_virial": [model.test_virial], "test_energy": [model.test_energy]}
        for attr in ATTRIBUTES:
            if attr in ARRAYS_ATTR:
                stars[attr].append(getattr(model, attr)[0][0])
                continue
            stars[attr].append(getattr(model, attr))
        LOGGER.debug("new values 'M: %s, R:%s, Z:%s, Omega_bk:%s' added", float(model.M), float(model.R), float(model.Z[0][0]), float(model.Omega_bk))

    if ARGS.save:
        save_default(stars)

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
        "--save",
        action="store_true",
        help="if used, save data to a storage file"
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
    parser.add_argument(
        "--filter",
        type=lambda s: s.split(','),
        help="filter out some value, expected as 'parameter,value'"
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
            logging.critical("'%s' isn't a path to a folder", folder)
            parser.error("Note a folder passed with '-f'")
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