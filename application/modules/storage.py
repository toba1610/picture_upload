from pathlib import Path

import shutil
from pathlib import Path, PurePath

import smbclient
from smbprotocol.exceptions import SMBException
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

def local_save(folder_name: str, filename: str, picture: FileStorage, upload_root: str) -> PurePath:

	safe_filename = check_save_filename(filename)
	safe_folder_name = check_save_folder_name(folder_name)

	destination_folder = Path(upload_root).expanduser() / safe_folder_name
	destination_folder.mkdir(parents=True, exist_ok=True)
	destination = destination_folder / safe_filename
	picture.save(destination)
	
	return destination

def remote_save(picture: FileStorage, folder_name: str, filename: str, upload_root: str, network_username: str | None = None, network_password: str | None = None) -> PurePath:

	network_root = PurePath(upload_root)
	server_share = network_root.drive.strip('\\').split('\\')
	if len(server_share) < 2 or not server_share[0]:
		raise ValueError('UPLOAD_ROOT muss ein UNC-Pfad mit Server und Freigabe sein.')
	if not network_username or not network_password:
		raise OSError('NETWORK_USERNAME und NETWORK_PASSWORD sind für SMB erforderlich.')

	safe_filename = check_save_filename(filename)
	safe_folder_name = check_save_folder_name(folder_name)

	server = server_share[0]
	destination_folder = network_root / safe_folder_name
	destination = destination_folder / safe_filename
	try:
		smbclient.register_session(
			server,
			username=network_username,
			password=network_password,
		)
		smbclient.makedirs(str(destination_folder), exist_ok=True)
		with smbclient.open_file(str(destination), mode='wb') as network_file:
			shutil.copyfileobj(picture.stream, network_file)
	except SMBException as error:
		raise OSError(f'Could not save picture to SMB server {server}.') from error
	return destination

def check_save_filename(filename: str) -> str:

	safe_filename = secure_filename(filename)

	if not safe_filename:
		raise ValueError('Der Dateiname ist ungültig.')

	return safe_filename

def check_save_folder_name(folder_name: str) -> str:

	safe_folder_name = secure_filename(folder_name.strip())

	if not safe_folder_name:
		raise ValueError('Der Ordnername enthält keine gültigen Zeichen.')

	return safe_folder_name

def save_picture(picture: FileStorage, folder_name: str, filename: str,	upload_root: str, network_username: str | None = None, network_password: str | None = None) -> PurePath:

	if upload_root.startswith(('\\\\', '//')):

		destination_path = remote_save(picture= picture, 
		                               filename= filename, 
									   folder_name= folder_name, 
									   upload_root= upload_root, 
									   network_username= network_username,
									   network_password= network_password)

	else:

		destination_path = local_save(picture= picture, 
		                              filename= filename, 
									  folder_name= folder_name, 
									  upload_root= upload_root)
		
	return destination_path
