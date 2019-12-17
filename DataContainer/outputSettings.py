class OutputSettings:
    """Container class for output settings.

    The following settings are provided:
    :param default_path: str = the path (just the folder, no file) where measurement files are created.
    :param default_filename: str = prefix that will be used for each measurement file. Should end with an _
    :param default_file_extension: str = defines the measurement file type. At the moment only csv files are
                                         supported (set this setting to "csv"). Maybe excel files will be
                                         supported later too
    :param separator: str = is only needed for csv files. Defines the character that tells the computer to
                            go to the next column. By default the separator is a comma (",").
    """

    def __init__(self, default_path: str, default_filename: str, default_file_extension: str, separator: str):
        """Initializes this class and stores the given values in their corresponding fields.

        :param default_path: str = the path (just the folder, no file) where measurement files are created.
        :param default_filename: str = prefix that will be used for each measurement file. Should end with an _
        :param default_file_extension: str = defines the measurement file type. At the moment only csv files are
                                             supported (set this setting to "csv"). Maybe excel files will be
                                             supported later too
        :param separator: str = is only needed for csv files. Defines the character that tells the computer to
                                go to the next column. By default the separator is a comma (",").
        """

        self.defaultPath = default_path
        self.defaultFilename = default_filename
        self.defaultFileExtension = default_file_extension
        self.separator = separator
