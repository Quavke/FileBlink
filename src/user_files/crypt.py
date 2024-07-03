from cryptography.fernet import Fernet
from tempfile import NamedTemporaryFile


def encrypt_file(file_) -> bytes:
    """
    Шифрует содержимое файла с использованием заданного секретного ключа.

    Args:
        file_: Загружаемый файл (UploadFile).

    Returns:
        Зашифрованные данные файла (bytes).
    """
    with open("key.key", "rb") as key_file:
        key = key_file.read()
    cipher = Fernet(key)
    with NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file_.file.read())
        temp_file_path = temp_file.name
    with open(temp_file_path, 'rb') as f:
        encrypted_data = cipher.encrypt(f.read())
    return encrypted_data


def decrypt_file(encrypted_data: bytes) -> bytes:
    """
    Дешифрует зашифрованные данные файла с использованием заданного секретного ключа.

    Args:
        encrypted_data: Зашифрованные данные файла (bytes).

    Returns:
        Дешифрованные данные файла (bytes).
    """
    with open("key.key", "rb") as key_file:
        key = key_file.read()
    cipher = Fernet(key)
    decrypted_data = cipher.decrypt(encrypted_data)
    # print(str(decrypted_data))
    return decrypted_data
