# Script that takes/asks for a directory containing 1d ester models
# then plot the radius in terms of Solar Mass
# separating curves in terms of Z

import os, re, argparse, logging
from matplotlib.pyplot import plot as plt
import numpy as np
import ester

ARGS = None

def main():
    # list files in the chosen folder
    files = os.listdir(ARGS.folder)
    # create a list of path (prepend ARGS.folder to files) of h5 files (regexp)
    models_paths = [os.path.join(ARGS.folder, f) for f in files if re.search(".h5$", f) is not None]

    stars = {}
    for path in models_paths:
        model = ester.star1d(path)
        key = str(model.Z[0])
        if not key in stars:
            stars.update({key : np.array([model.M, model.R])})
            logging.info("new key '%s' added to stars dict", key)
            logging.debug("new value 'M: %s, R:%s' added to stars dict at key '%s'", float(model.M), float(model.R), key)
        else:
            stars[key] = np.append(stars[key], [model.M,model.R])
            logging.debug("new value 'M: %s, R:%s' added to stars dict at key '%s'", float(model.M), float(model.R), key)
    print(stars)

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

    if ARGS is None:
        logging.critical("Arg parsing failed, exiting...")
        exit(1)

    if not os.path.exists(ARGS.folder) or os.path.isfile(ARGS.folder):
        logging.warning("'%s' isn't a directory path, use working directory")

    level = (5 - ARGS.verbose)*10
    logging.getLogger().setLevel(level)

    try:
        main()
    except KeyboardInterrupt:
        logging.error("Detected CTRL+C, exiting...")