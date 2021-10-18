# EnergyPlus, Copyright (c) 1996-2021, The Board of Trustees of the University
# of Illinois, The Regents of the University of California, through Lawrence
# Berkeley National Laboratory (subject to receipt of any required approvals
# from the U.S. Dept. of Energy), Oak Ridge National Laboratory, managed by UT-
# Battelle, Alliance for Sustainable Energy, LLC, and other contributors. All
# rights reserved.
#
# NOTICE: This Software was developed under funding from the U.S. Department of
# Energy and the U.S. Government consequently retains certain rights. As such,
# the U.S. Government has been granted for itself and others acting on its
# behalf a paid-up, nonexclusive, irrevocable, worldwide license in the
# Software to reproduce, distribute copies to the public, prepare derivative
# works, and perform publicly and display publicly, and to permit others to do
# so.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# (1) Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
# (2) Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
# (3) Neither the name of the University of California, Lawrence Berkeley
#     National Laboratory, the University of Illinois, U.S. Dept. of Energy nor
#     the names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# (4) Use of EnergyPlus(TM) Name. If Licensee (i) distributes the software in
#     stand-alone form without changes from the version obtained under this
#     License, or (ii) Licensee makes a reference solely to the software
#     portion of its product, Licensee must refer to the software as
#     "EnergyPlus version X" software, where "X" is the version number Licensee
#     obtained under this License and may not use a different name for the
#     software. Except as specifically required in this Section (4), Licensee
#     shall not use in a company name, a product name, in advertising,
#     publicity, or other promotional activities any name, trade name,
#     trademark, logo, or other designation of "EnergyPlus", "E+", "e+" or
#     confusingly similar designation, without the U.S. Department of Energy's
#     prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import sys

# the EnergyPlusInstallRoot should be added to the search path prior to trying to import anything else
# sys.path.insert(0, '/path/to/EnergyPlusInstallRoot')
sys.path.insert(0, u"C:\EnergyPlusV9-5-0")

from pyenergyplus.api import EnergyPlusAPI

one_time = True
zone_temp_sensor = 0
power_level_actuator = 0


def time_step_handler(state):
    global one_time, zone_temp_sensor, power_level_actuator 
    sys.stdout.flush()
    if one_time:
        if api.exchange.api_data_fully_ready(state):
            # val = api.exchange.list_available_api_data_csv()
            # with open('/tmp/data.csv', 'w') as f:
            #     f.write(val.decode(encoding='utf-8'))
            zone_temp_sensor = api.exchange.get_variable_handle(
                state, u"Zone Air Temperature", u"ZONE ONE"
            )
            power_level_actuator = api.exchange.get_actuator_handle(
                state, "OtherEquipment", "Power Level", "TestOtherEquipment"
            )
            if zone_temp_sensor == -1 or power_level_actuator == -1: 
                print(f'sensor or actuator not found temp = {zone_temp_sensor} and pow_level={power_level_actuator}')
                sys.exit(1)
            one_time = False
    zone_temp = api.exchange.get_variable_value(state, zone_temp_sensor)
    # print("Reading outdoor temp via getVariable, value is: %s" % zone_temp)
    if zone_temp < 22:
        api.exchange.set_actuator_value(state, power_level_actuator, 0.0)
    else: 
        api.exchange.set_actuator_value(state, power_level_actuator, 1300.0)

    # sim_time = api.exchange.current_sim_time(state)
    # print("Current sim time is: %f" % sim_time)
    if api.exchange.zone_time_step_number(state) == 1:
        n = api.exchange.num_time_steps_in_hour(state)
        tomorrow_db = api.exchange.tomorrow_weather_outdoor_dry_bulb_at_time(state, 3, 2)
        # print(f"Num time steps in hour = {n}; Tomorrow's hour 3, timestep 2 temp is: {tomorrow_db}")


api = EnergyPlusAPI()
state = api.state_manager.new_state()
api.runtime.callback_end_zone_timestep_after_zone_reporting(state, time_step_handler)
api.exchange.request_variable(state, u"Zone Air Temperature", u"ZONE ONE")
print("initialization done")
# trim off this python script name when calling the run_energyplus function so you end up with just
# the E+ args, like: -d /output/dir -D /path/to/input.idf
api.runtime.run_energyplus(state, sys.argv[1:])
