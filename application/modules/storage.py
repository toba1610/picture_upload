from pathlib import Path

import shutil
from pathlib import Path, PurePath, PureWindowsPath

import smbclient
from smbprotocol.exceptions import SMBException
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


def save_picture(
	picture: FileStorage,
	folder_name: str,
	filename: str,
	upload_root: str,
	network_username: str | None = None,
	network_password: str | None = None,
) -> PurePath:
	safe_folder_name = secure_filename(folder_name.strip())
	safe_filename = secure_filename(filename)
	if not safe_folder_name:
		raise ValueError('Der Ordnername enthält keine gültigen Zeichen.')
	if not safe_filename:
		raise ValueError('Der Dateiname ist ungültig.')

	if upload_root.startswith(('\\\\', '//')):
		network_root = PureWindowsPath(upload_root)
		server_share = network_root.drive.strip('\\').split('\\')
		if len(server_share) < 2 or not server_share[0]:
			raise ValueError('UPLOAD_ROOT muss ein UNC-Pfad mit Server und Freigabe sein.')
		if not network_username or not network_password:
			raise OSError('NETWORK_USERNAME und NETWORK_PASSWORD sind für SMB erforderlich.')

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

	destination_folder = Path(upload_root).expanduser() / safe_folder_name
	destination_folder.mkdir(parents=True, exist_ok=True)
	destination = destination_folder / safe_filename
	picture.save(destination)
	return destination
