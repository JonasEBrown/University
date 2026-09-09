from ..my_types import *


class CMap:
    """
        A colormap wrapper that allows for color manipulation.
    """
    def __init__(self, cmap: CMapFunc | str = "prism", segments: int = 1):
        """
            Initialise a CMap with a colormap and number of segments.

            Args:
                cmap (CMapFunc | str): The colormap to use. Can be a string name or a callable.
                segments (int): The number of segments in the colormap.
        """
        # Convert string colormap names to actual colormap objects.
        if type(cmap) is str:
            cmap = plt.get_cmap(cmap) # Get colormap by name from matplotlib.
        self._cmap = cmap # Store the colormap callable.
        self._segments = segments # Store the number of segments.

    def darken_desaturate(self, factor=0.85) -> CMapFunc:
        """
            Darken and desaturate the colormap by a given factor.

            Args:
                factor (float): The factor by which to darken and desaturate the colors. 

            Returns:
                CMapFunc: The modified colormap function.
        """
        # Generate a list of colors from the original colormap.
        colors: list[ColorValue] = [self._cmap(index) for index in range(self._segments)]
        # Modify each color.
        for index, color in enumerate(colors):
            h, l, s = colorsys.rgb_to_hls(*color[:-1]) # Convert RGB to HLS.
            l *= factor # Darken.
            s *= factor # Desaturate.
            # Convert back to RGB and update the color.
            colors[index] = (*colorsys.hls_to_rgb(h, l, s), color[-1])
        self._cmap = lambda index: colors[index] # Wrap the new colormap into a function.
        return self._cmap # Return the modified colormap function.

    def __call__(self, index: int) -> ColorValue:
        """
            Make the CMap instance callable, forwarding calls to the underlying colormap.

            Args:
                index (int): The index of the color to retrieve.
            
            Returns:
                ColorValue: The color at the specified index.
        """
        return self._cmap(index) # Call the underlying colormap function.