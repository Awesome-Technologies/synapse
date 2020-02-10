## Prerequisites

	pip3 install pyyaml requests qrcode fpdf pillow
	
This script uses the Admin API v2 which was introduced with Synapse 1.8.0
	
## Usage

### Dry run

It's recommended to perform a dry run first, to check if the given admin user has the rights to register users and all dependencies for the tool are installed correctly. Also check the correct encoding of german umlauts in the generated PDF. The script automatically performs a dry run if the corresponding flag (`--no-dry-run`) is not set.

 	python3 batch_register_matrix_users.py -u <Admin username> -p <Admin password> -f <Path to CSV file> <Homeserver URL>

or

	python3 batch_register_matrix_users.py -f <Path to CSV file> <Homeserver URL>

The script will generate a folder named named after the homeserver url (with `.`
 converted to `_`, eg. `https://matrix.example.org` will become `matrix_example_org`). Inside the folder two files will be created: Userlist.pdf and Userlist_QR.pdf. Additionaly a folder is created named "qr" where all the generated qr codes are saved, named with an increasing number that represents the position on the users list, followed by the displayname and the user id (eg. `002_John_Doe_c5g43rzy.png`). The folder structure looks like this:
 
	.
	+-- matrix_example_org
	|   +-- Userlist.pdf
	|   +-- Userlist_QR.pdf	
	|   +-- qr
	|   |   +-- 000_John_Doe_k3n2occp.png
	|   |   +-- 001_Jane_Doe_is83n7fs.png
	|   |   +-- 002_Jonny_Doe_p29c7skw.png
	...	

### QR code generation
If the flag `--qr-only` is provided, the script will use the data from the csv file to generate the PDFs with QR codes and userlist without registering the users at the server.

### Productive use

	python3 batch_register_matrix_users.py -u <Admin username> -p <Admin password> -f <Path to CSV file> --no-dry-run <Homeserver URL>

or

	python3 batch_register_matrix_users.py -f <Path to CSV file> --no-dry-run <Homeserver URL>
	
## CSV File format
### Format

	first_name;last_name;username;password;admin;user_type

When `username` is left empty a 8-character username is generated, containing lowercase letters and digits.

When `password` is left empty a 20-character password is generated, containing lowercase letters and digits.

User is only set as admin when the `admin` field contains `yes`.

User is set as guest when `user_type` field contains `guest`, otherwise the user will be a normal user.

### Encoding
Perform a dry run first to check if all characters (especially german umlauts) are encoded correctly on the console output and the generated PDF file. On Windows based systems the file should be saved with ANSI encoding.

## Logo
A logo can be provided using the parameter `-l <path to logo>`. If no logo file is specified the script will use the file `logo.png` in the scripts folder.