Kudasai.py

Original Author: thevoidzero#4686
Refactored and Maintained by: Seinu#7854
Contributions by: SnOrT NeSqUiK™#9775

Run the pip commands listed in requirements.txt before running Kudasai.

Python Version: 3.7.6-3.11.2

Used to make Classroom of the Elite translation easier by preprocessing the Japanese text (optional auto translation using deepL API).

Derived from https://github.com/Atreyagaurav/mtl-related-scripts

CmdLineArgs
Argument 1: Path to a .txt file that needs to be preprocessed
Argument 2: Path to JSON Criteria

Output: KudasaiOutput (folder on the desktop)

KudasaiOutput contains:

jeCheck.txt (a txt file for j-e checkers to cross-check sentences that were translated by deepL)
output.txt (a txt file containing Kudasai's output, basically what Kudasai replaced)
preprocessedText.txt (a txt file containing the results of Kudasai's preprocessing)
tlDebug.txt (a txt file containing debug material for the developer)
translatedText.txt (a txt file containing the results of Kaiseki.py, the auto translation module)

To use

Step 1: Open CMD
Step 2: Copy the path of Kudasai.py to cmd and type a space.
Step 3: Copy the path of .txt file you want to preprocess to cmd and type a space.
Step 4: Copy the path of replacements.json to CMD
Step 5: Press enter.

Any questions or bugs, please email Seinuve@gmail.com
