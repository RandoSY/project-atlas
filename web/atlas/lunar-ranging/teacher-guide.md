# The Echo Experiment — teacher/operator guide v1.0
## Question
How accurately can we recover a known distance from a measured echo time? How does a clock limit our knowledge?
## Build
Arduino Uno (5 V), HC-SR04, jumper wires, meterstick, flat rigid target, USB cable; thermometer optional. No shield library is required. A typical multifunction shield may expose A4/A5; check the actual schematic and continuity. If unavailable, remove shield or choose two verified unused pins and change the sketch. Connect VCC to 5 V, GND to GND, TRIG to A4, ECHO to A5. Do not connect 5 V echo directly to 3.3 V MCUs. Power off while wiring. Shield display intentionally not driven in v1.0 to avoid clone-specific pin conflicts.
## Operate
Open echo_lab/echo_lab.ino in Arduino IDE; select Uno and port, upload. Close Serial Monitor. Open exhibit Lab tab in desktop Chrome/Edge over HTTPS, Connect USB, select the port, enter temperature and independently measured reference mm. The stream is sequence,millis,echo_us; zero means no valid echo. For browsers without Web Serial, use the demo or capture serial CSV using the Arduino Serial Monitor and calculate manually.
## Student procedure (CAP)
1. Predict echo time at 1 m using 343 m/s. Measure reference from transducer face to target, perpendicular to beam.
2. At 200, 400, 600, 800 and 1000 mm collect 100 valid readings per distance. Clear between runs, export each CSV. Record temperature, target geometry and any timeouts. Keep the setup fixed during each run.
3. Calculate v=331.3+0.606T m/s and d_mm=v*echo_us/2000. Compare average against ruler, compute sample standard deviation and bias. Resolution is not accuracy. Estimate reference uncertainty.
4. Repeat at timer quantization 10, 100 and 1000 microseconds. This is simulated quantization of captured pulse widths, not changing the MCU clock. Compare error, retain raw readings. pulseIn is software-timed and has its own error.
5. Fit measured vs reference distance; test slope/intercept on a held-out distance. Do not confuse calibration and validation.
6. Substitute c=299792458 m/s and calculate range uncertainty for 1 ns and 1 ps. Explain why sound cannot propagate through space.
## Teacher notes
At 20 C, 1 m round trip is about 5.82 ms. At 1 m light takes 6.67 ns. A 1 mm light range increment corresponds to 6.67 ps. The lunar 2.56 s figure uses mean center separation, not actual observatory-to-reflector range. Actual lunar data require atmospheric/geometric/relativistic corrections and calibration.
## Why lunar reflectors remain accessible
The Moon rotates once per orbit (about 27.3 Earth days). Tidal locking keeps approximately the same hemisphere facing Earth, so the near-side Apollo reflectors do not pass onto the far side each month. Corner cubes return light approximately toward its source without powered tracking. The Moon must still be above the station's horizon, with suitable observing conditions; libration and viewing geometry also affect ranging.
Classroom demonstration: place a chair at the center of the room as Earth. Walk around it once while always facing it, holding a hand in front as the reflector. Compare with walking around without rotating relative to the room. Ask students to explain why one full rotation per orbit keeps the reflector facing Earth.
## Optional extension
Compare a VL53L4CD I2C sensor with the ruler and ultrasound. It reports internally processed direct optical ToF; not an external MCU picosecond counter. Do not aim lasers at the sky.
## Assessment
Explain why tidal locking keeps near-side reflectors accessible, explain the factor of two, graph bias and scatter, distinguish resolution and accuracy, identify environmental effects, publish raw CSV and a defensible uncertainty statement.
## Release status
Source prototype; hardware and browser serial integration not bench-validated. Demo measurements are synthetic.
