################################################################################
# ecm_json_format_check.py
#
# Verify the structure in of a energy conservation measure (ECM) json file is as
# expected.
#
# based on documentation
#
# https://scout-bto.readthedocs.io/en/latest/ecm_reference.html
#
################################################################################

import json
import sys
import os
import warnings

################################################################################
class ECMJSON:
    def __repr__(self):
        return "ECMJSON"

    def __str__(self):
        return "ecm_json_path: % s\n" % (self.ecm_json_path)

    def __init__(self, ecm_json_path):
        if not ecm_json_path:
            sys.exit("specify ecm_json_path")
        else:
            self.ecm_json_path = ecm_json_path

        with open(self.ecm_json_path) as f:
            self.ecm_json = json.load(f)
            f.close()


        # verify keys are as expected
        self.key_errors = []
        self.key_warnings = []
        self.verify_primary_keys()
        self.verify_name_key()
        self.verify_climate_zone_key()
        # TODO: build many more verify_.*_key() functions
        if self.key_warnings:
            warnings.warn(str(self.key_warnings))
        if self.key_errors:
            print(str(self.key_errors))
            sys.exit()

    ############################################################################
    def verify_primary_keys(self):
        """
        Verify the top level keys in the json file are unique and in the list of
        required or recommended keys.  Also, report any unexpected primary level
        keys.
        """

        # If a required element is not found an error is thrown.  If a
        # recommended element is missing a warning is thrown.
        required_keys = ["name", "climate_zone", "bldg_type", "structure_type",
                "end_use", "fuel_type", "technology", "market_entry_year",
                "market_exit_year", "energy_efficiency",
                "energy_efficiency_units", "installed_cost", "cost_units",
                "product_lifetime", "product_lifetime_units", "measure_type",
                "fuel_switch_to", "market_scaling_fractions"]
        recommended_keys = ["market_entry_year_source",
                "market_exit_year_source", "energy_efficiency_source",
                "installed_cost_source", "product_lifetime_source",
                "market_scaling_fractions_source", "_description", "_notes",
                "_added_by", "_updated_by"]

        e =  [e for e in required_keys if e not in list(self.ecm_json)]
        if e:
            self.key_errors.append(str(e) + " required keys are not in " +\
                    self.ecm_json_path)

        e =  [e for e in recommended_keys if e not in list(self.ecm_json)]
        if e:
            self.key_warnings.append(str(e) + " recommended element(s)" +\
                    " are not found in " + self.ecm_json_path)

        e = [e for e in list(self.ecm_json) if ((e not in required_keys) and
                                           (e not in recommended_keys))]
        if e:
            self.key_warnings.append(str(e) + " is(are) unexpected key(s) in "\
                    + self.ecm_json_path)

    ############################################################################
    def verify_name_key(self):
        """ Verify the structure and contents of the name key """

        if not isinstance(self.ecm_json["name"], str):
            self.key_errors.append("\"name\": should be a str in " +
                    self.ecm_json_path)

        if not self.ecm_json["name"] ==\
                os.path.splitext(os.path.basename(self.ecm_json_path))[0]:
            self.key_warnings.append("\"name\" differes from file name " +
                    self.ecm_json_path)

        if len(self.ecm_json["name"]) > 55:
            self.key_warnings.append(
                    "\"name\" exceeds the recommended maximum of 55 characters")

    ############################################################################
    def verify_climate_zone_key(self):
        """
        climate_zone should exist in each ecm json file with values as either a
        single string "all" or a list of AIA, EMM, or contintintal states.
        """

        # Define valid climate zones
        valid_czs = {
                "AIA" : ["AIA_CZ1", "AIA_CZ2", "AIA_CZ3", "AIA_CZ4", "AIA_CZ5"],
                "EMM" : ["TRE", "FRCC", "MISW", "MISC", "MISE", "MISS", "ISNE",
                    "NYCW", "NYUP", "PJME", "PJMW", "PJMC", "PJMD", "SRCA",
                    "SRSE", "SRCE", "SPPS", "SPPC", "SPPN", "SRSG", "CANO",
                    "CASO", "NWPP", "RMRG", "BASN"],
                "States" : ["AL", "AZ", "AR", "CA", "CO", "CT", "DE", "DC",
                    "FL", "GA", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME",
                    "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
                    "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
                    "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI",
                    "WY"]
        }

        # Check Acceptable Climate Zone
        if isinstance(self.ecm_json["climate_zone"], str):
            if not (self.ecm_json["climate_zone"] == "all"):
                self.key_errors.append("In " + ecm_json_path +
                ": single string `climate_zone` " +
                "definition may only be: `\"climate_zone\": \"all\"`")
        elif isinstance(self.ecm_json["climate_zone"], list):
            cz_test = []
            for cz in self.ecm_json["climate_zone"]:
                cz_test.append([cz in valid_czs[j] for j in valid_czs])
            if not all([ sum(j) == 1 for j in cz_test]):
                self.key_errors.append(
                        "More than one Climate Zone Region specificaiton in " +
                        self.ecm_json_path)
        else:
            self.key_errors.append("Unexpected `climate_zone` in " +
                    self.ecm_json_path)


################################################################################
###                                   main                                   ###
def main():
    ECMJSON(str(sys.argv[1]))

if __name__ == "__main__":
    main()

################################################################################
###                               End of File                                ###
################################################################################

