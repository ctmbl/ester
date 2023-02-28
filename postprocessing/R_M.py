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
    color = "red"
    STYLES = iter(["+", "x"])

    ax.tick_params(axis='y', labelcolor=color)
    ax.set_xlabel("M/M_sun")
    ax.set_ylabel("R/R_sun")

    for key, value in stars.items():
        try:
            ax.plot("M", "R", next(STYLES), data=stars[key], label=f"{key} Radius", color=color)
        except StopIteration:
            LOGGER.error("Not enough STYLES to plot each set of datas, stopped at key '%s'", key)

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
            LOGGER.error("Not enough STYLES to plot each set of datas, stopped at key '%s'", key)

    ax.legend(loc='upper right')

def main():
    # list files in the chosen folder
    files = os.listdir(ARGS.folder)
    # create a list of path (prepend ARGS.folder to files) of h5 files (regexp)
    models_paths = [os.path.join(ARGS.folder, f) for f in files if re.search(".h5$", f) is not None]
    LOGGER.debug("Found %s models: [%s]", len(models_paths), models_paths)

    stars = {}
    # the list of attributes to extract from each 1D model
    attributes = ["M", "R", "test_virial", "test_energy"]
    for path in models_paths:
        model = ester.star1d(path)
        LOGGER.debug("parsing model file at path '%s'", path)
        key = str(model.Z[0])

        if not key in stars:
            # TEMPLATE:  {key : {"M": [model.M], "R": [model.R], "test_virial": [model.test_virial], "test_energy": [model.test_energy]}}
            stars.update({key: {}})

            for attr in attributes:
                stars[key].update({attr: [getattr(model, attr)]})

            LOGGER.info("new key '%s' added to stars dict", key)
            LOGGER.debug("new values 'M: %s, R:%s' added to stars dict at key '%s'", float(model.M), float(model.R), key)
        else:
            for attr in attributes:
                stars[key][attr].append(getattr(model, attr))

            LOGGER.debug("new values 'M: %s, R:%s' added to stars dict at key '%s'", float(model.M), float(model.R), key)

    # Normalize values on sun parameters
    # Pass test_* to absolute values (to be displayed on log scale)
    for key in stars:
        stars[key]['M'] = list(map(lambda x: x/ester.M_SUN, stars[key]['M']))
        stars[key]['R'] = list(map(lambda x: x/ester.R_SUN, stars[key]['R']))
        stars[key]['test_virial'] = list(map(lambda x: abs(x), stars[key]['test_virial']))
        stars[key]['test_energy'] = list(map(lambda x: abs(x), stars[key]['test_energy']))

    fig, ax1 = plt.subplots()
    plot_R_fM(stars, ax1)
    ax2 = ax1.twinx()
    plot_tests_fM(stars, ax2)
    
    plt.show()

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