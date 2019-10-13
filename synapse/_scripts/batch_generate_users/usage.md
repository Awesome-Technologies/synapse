## Prerequisites

	pip3 install pyyaml requests qrcode fpdf pillow
	
## Usage

### Dry run

It's recommended to perform a dry run first, to check if the given admin user has the rights to register users and all dependencies for the tool are installed correctly. Also check the correct encoding of german umlauts in the generated PDF. The script automatically performs a dry run if the corresponding flag (`--no-dry-run`) is not set.

 	python3 batch_register_matrix_users.py -u <Admin username> -p <Admin password> -f <Path to CSV file> <Homeserver URL>

or

	python3 batch_register_matrix_users.py -f <Path to CSV file> <Homeserver URL>
	
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