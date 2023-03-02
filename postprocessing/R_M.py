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
    Z = []
    M = []
    R = []

    if len(models_paths) == 0:
        LOGGER.warning("No models found in this directory, using older values for M, R and Z lists")
        M = [95.00000000000001, 95.00000000000001, 4.0, 100.0, 95.00000000000001, 170.0, 35.0, 95.00000000000001, 108.00000000000001, 60.0, 95.00000000000001, 30.0, 95.00000000000001, 95.00000000000001, 20.0, 95.00000000000001, 160.0, 105.0, 120.0, 2.9999999999999996, 250.0, 70.0, 105.0, 95.00000000000001, 150.0, 95.00000000000001, 95.00000000000001, 95.00000000000001, 90.0, 95.00000000000001, 54.99999999999999, 130.0, 109.99999999999999, 10.0, 95.00000000000001, 50.0, 95.00000000000001, 25.0, 95.00000000000001, 300.0, 140.0, 45.0, 200.0, 100.0, 95.00000000000001, 2.0, 40.0, 95.00000000000001, 95.00000000000001, 95.00000000000001, 15.0, 300.0, 95.00000000000001, 7.0, 80.0, 95.00000000000001, 95.00000000000001, 5.0, 85.0, 41.99999999999999]
        R = [8.843585329375681, 14.871262089642036, 2.3090136110854886, 4.526973611488149, 9.632180929023002, 6.012094606363337, 7.813408191898322, 15.45683756197053, 18.062580453553284, 10.785581228983071, 14.364725459330586, 7.162419393783571, 7.581795592829309, 13.244651308204029, 5.716273567471856, 6.477795175955188, 5.819360439402384, 17.372822448972247, 4.988455877157205, 1.9673256954307219, 7.401872764673879, 11.967125586166132, 4.645888428459556, 13.89967742425352, 5.621196100925406, 10.602703970436735, 8.71142172412895, 15.151768537421278, 14.645267117761248, 8.441334680802003, 10.20547862478921, 5.206412573143348, 4.762336331635683, 3.8790920419525956, 5.500563611332647, 9.624312582848573, 4.405385580909005, 6.469523604020436, 4.641764190345712, 8.168506696604064, 5.417083650276054, 9.036158053522982, 6.561911792819359, 16.351169543353627, 14.611114013702156, 1.601472461918693, 8.434832714552725, 14.128027878607494, 11.857344020760985, 13.029348829861226, 4.870924002783196, 7.60117721446439, 13.460523335325668, 3.170979364409926, 13.226894887509095, 11.251402255618034, 10.309525560516645, 2.6196008359296346, 13.909225070590054, 8.677365914485128]
        Z = [-4.000000000000048, -1.7447274948966935, -1.6989700043360183, -8.301029993481755, -3.4559319556497035, -8.301029993481755, -1.6989700043360183, -1.6989700043360183, -1.6989700043360183, -1.6989700043360183, -1.7958800173440748, -1.6989700043360183, -4.999999999999566, -1.9586073148417746, -1.6989700043360183, -6.00000000001162, -8.301029993481755, -1.6989700043360183, -8.301029993481755, -1.6989700043360183, -8.301029993481755, -1.6989700043360183, -8.301029993481755, -1.8538719643217616, -8.301029993481755, -2.8860566476931555, -4.096910013007923, -1.7212463990471707, -1.6989700043360183, -4.301029995664029, -1.6989700043360183, -8.301029993481755, -8.301029993481755, -1.6989700043360183, -6.999999999987511, -1.6989700043360183, -8.301029993481755, -1.6989700043360183, -8.000000000228594, -8.301029993481755, -8.301029993481755, -1.6989700043360183, -8.301029993481755, -1.6989700043360183, -1.7695510786217257, -1.6989700043360183, -1.6989700043360183, -1.8239087409443184, -2.3279021420642843, -1.9999999999999996, -1.6989700043360183, -8.698970004564613, -1.920818753952375, -1.6989700043360183, -1.6989700043360183, -2.5686362358410157, -3.0457574905606695, -1.6989700043360183, -1.6989700043360183, -1.6989700043360183]

    # the list of attributes to extract from each 1D model
    attributes = ["M", "R", "test_virial", "test_energy"]
    for path in models_paths:
        if re.search("2d", path) is not None:
            LOGGER.warning("Ignore %s, seems to be 2D model", path)
            continue

        model = ester.star1d(path)
        LOGGER.debug("parsing model file at path '%s'", path)
        key = str(model.Z[0])

        if model.Z[0] != 0:
            Z.append(float(np.log10(model.Z[0])))
            M.append(model.M/ester.M_SUN)
            R.append(model.R/ester.R_SUN)

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

    if ARGS.print:
        print("stars:", stars)
        print("M:", M)
        print("R:", R)
        print("Z:", Z)

    # Normalize values on sun parameters
    # Pass test_* to absolute values (to be displayed on log scale)
    for key in stars:
        stars[key]['M'] = list(map(lambda x: x/ester.M_SUN, stars[key]['M']))
        stars[key]['R'] = list(map(lambda x: x/ester.R_SUN, stars[key]['R']))
        stars[key]['test_virial'] = list(map(lambda x: abs(x), stars[key]['test_virial']))
        stars[key]['test_energy'] = list(map(lambda x: abs(x), stars[key]['test_energy']))

    fig = plt.figure()
    if ARGS.scatterplot:
        ax = fig.add_subplot(projection='3d')
        ax.scatter(M, Z, R, marker='^')

        ax.set_xlabel('M/M_SUN')
        ax.set_zlabel('R/R_SUN')
        ax.set_ylabel('log(Z)')
    else:
        ax = fig.add_subplot()
        plot_R_fM(stars, ax)
        ax = ax.twinx()
        plot_tests_fM(stars, ax)

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