# SE20UARI026_SE20UARI057_SE20UARI135

Group Members 
Avani - SE20UARI026
Geha - SE20UARI057
Samvidha - SE20UARI135 	


We have used Fingerprint sensor on a Raspberry Pi captures and processes fingerprint data to verify or identify individuals based on their unique fingerprint pattern.  

Fingerprint Sensor : also known as fingerprint scanner/ reader device that captures and analyzes the unique patterns found on an individual's fingertip. Commonly used for authentication, security and identity verification.

Overview  
Components Involved  
Raspberry Pi, Fingerprint sensor, Jumper wires,Power source, Monitor 

Hardware Connection: 
Connected the ground, power, serial communication pins of the fingerprint sensor module to the Raspberry Pi using jumper wires.

Software and capturing fingerprints - 
Opened terminal on the Raspberry Pi and installed necessary libraries for the fingerprint sensor i.e Adafruit
Code - python script to enroll fingerprints, added an authentication to verify fingerprints ((explained in detailed))

Working of  fingerprint recognition for authentication : 
 Compare the captured fingerprint template with a single stored template to determine if they match. If they do, grant access.
Provide feedback to the user, such as a green LED for access granted or a red LED for access denied.

