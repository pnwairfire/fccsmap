"""fccsmap.tileslookup
"""

__author__      = "Joel Dubowy"

from . import BaseLookUp

__all__ = [
    'FccsTilesLookUp'
]

class FccsTilesLookUp(BaseLookUp):

    # OPTIONS_DOC_STRING used by Constructor docstring as well as
    # script helpstring
    OPTIONS_STRING = """
         - is_alaska -- Whether or not location is in Alaska; boolean
         - is_canada -- Whether or not location is in Canada; boolean
         - is_hawaii -- Whether or not location is in Hawaii; boolean
         - tiles_directory --
         - spatial_index_file --
    """

    def __init__(self, **options):
        """Constructor

        Valid options:

        {}

        """.format(self.OPTIONS_STRING + self.ADDITIONAL_OPTIONS_STRING)

        # TODO: load spatial index
        # TODO: load set tiles directory
        # TODO: determine projection

        super().__init__(**options)


    ##
    ## Helper methods
    ##

    def _look_up(self, geo_data):
        raise NotImplementedError("Tiles based FCCS look-up not yet implemented")