# Smart Irrigation Controller
Throughout summer in wester europe, weather can become pretty toasty, pretty fast.
To prevent our plants to burn alive while I'm happily going in vacations, usually to someplace where the temperature is more comfortable than where I live, I drafted this little project from parts that are (kind of) generally available in tinkerers drawers.

Of course, this project is nothing fancy nor especially clever, but rather an attempt to put parts together at last minute and catch the train before it leaves!

# What to expect from it
The plan is to design an automated (and hopefully somewhat resilient) micro platform that'll be composed of:
* A 12V motor that'll actuate a modified pinion-rack system through a custom built gearbox
* The electronics hardware (either PCB, free form wiring, etc) responsible to drive the motor
* A tiny microcontroller based on any Arduino Nano/UNO will do the job just fine
* A single LiHV cell salvaged from old computer batteries
* An auto-close system in case of failure (passive system, won't rely on any powered device)

From the software side, the goal is to set custom time frames, where the tap would be kept opened.
Note that depending on the design, extended "Opened" period of time may not exceed some threshold (a DC motor that does not spin will exhibit very low impedance path, causing a surge in current and then internal heating.)
This is fine if kept under close control (open loop strategies may work very well: like keep it open for 2 minutes, close, wait for an hour and start over).

## Important Notes (safety disclaimer)
I don't expect this system to fail dramatically (burst in flames, leaves the tap opened indefinitely, throws out a nuclear reaction in your kitchen sink), but make sure (if you decide to reuse the design) to take the appropriate safety measures.
This project is published as-is with no warranties of any sort; I cannot be held responsible if anything goes wrong :)

# License notes
This project contains mixed contents such as:
* [Electronic](Electronics/) designs
* [Mechanical](Mechanical/) designs
* [Software](Software/) source files

Electronic and Mechanical sources are covered by the CERN OHL V2 Permissive license.
Software is covered by the MIT License.