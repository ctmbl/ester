#ifndef WITH_CMAKE
#include "ester-config.h"
#endif
#include "physics.h"
#include "parser.h"


double_map initial_composition(double X, double Z) {
	double_map comp;
	file_parser fp;
	
	double Y = 1. - (X + Z);

	comp["H"] = X;
	comp["He3"] = 3.15247417638132e-04 * Y;
	comp["He4"] = Y - comp["He3"];

	// TODO: change this hardcoded
	char file[] = "metal-mix.cfg";

	char* arg = NULL;
	char* val = NULL;

	if(!fp.open(file)){
		printf("Can't open configuration file %s\n", file);
		perror("Error:");
		exit(1);
	} else {
		int line;
		while(line = fp.get(arg,val)) {
			if(val == NULL){
				printf("Syntax error in configuration file %s, line %d\n", file, line);
				exit(1);
			}
			comp[arg] = Z * atof(val);
		}
	}
	fp.close();
	comp["Ex"] = 1 - comp.sum();

	return comp;
}

matrix composition_map::X() const {

	return (*this)["H"];

}

matrix composition_map::Y() const {

	return (*this)["He3"]+(*this)["He4"];

}

matrix composition_map::Z() const {

	return 1.-X()-Y();

}

