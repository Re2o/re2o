import subprocess


def user_printing_path(instance, filename):
    """
    Defines the path where will be uploaded the files
    Currently MEDIA_ROOT/printings/user_<id>/<filename>
    """
    # File will be uploaded to MEDIA_ROOT/printings/user_<id>/<filename>
    return 'printings/user_{0}/{1}'.format(instance.user.id, filename)



def pdfinfo(file_path):
    """
    Uses pdfinfo to extract the PDF meta information.
    Returns metainfo in a dictionary.
    requires poppler-utils
    """
    def _extract(row):
        """Extracts the right hand value from a : delimited row"""
        row=row.decode()
        return row.split(':', 1)[1].strip()

    output = {}

    labels = ['Title', 'Author', 'Creator', 'Producer', 'CreationDate', 'ModDate',
              'Tagged', 'Pages', 'Encrypted', 'Page size',
              'File size', 'Optimized', 'PDF version']

    cmd_output = subprocess.check_output(['/usr/bin/pdfinfo', file_path])
    for line in cmd_output.splitlines():
        for label in labels:
            if label in line.decode():
                output[label] = _extract(line)

    return output
