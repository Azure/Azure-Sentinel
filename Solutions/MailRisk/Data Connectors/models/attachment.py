from .model import Model


class Attachment(Model):
    # SIC: Attachment is a sub-resource under emails
    RESOURCE_URL = 'emails'

    def __init__(self, filename: str, extension: str, content_type: str, content_id: str, is_inline: str,
                 size_bytes: int, md5_hash: str, sha1_hash: str, sha256_hash: str, last_modified_at: str,
                 download_screenshot: str, download_file: str):
        self.filename = filename
        self.extension = extension
        self.content_type = content_type
        self.content_id = content_id
        self.is_inline = is_inline
        self.size_bytes = size_bytes
        self.md5_hash = md5_hash
        self.sha1_hash = sha1_hash
        self.sha256_hash = sha256_hash
        self.last_modified_at = last_modified_at
        self.download_screenshot = download_screenshot
        self.download_file = download_file

    @classmethod
    def from_json(cls, json_item):
        return cls(filename=json_item['filename'],
                   extension=json_item['extension'],
                   content_type=json_item['content_type'],
                   content_id=json_item['content_id'],
                   is_inline=json_item['is_inline'],
                   size_bytes=json_item['size_bytes'],
                   md5_hash=json_item['md5_hash'],
                   sha1_hash=json_item['sha1_hash'],
                   sha256_hash=json_item['sha256_hash'],
                   last_modified_at=json_item['last_modified_at'],
                   download_screenshot=json_item['download_screenshot'],
                   download_file=json_item['download_file'])

    def __str__(self):
        return self.filename
