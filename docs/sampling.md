# Sampling

## When area is not specified

When a single point is passed in as input, the default behavior of
`FccsLookUp.look_up` is to determine the distribution of fuelbeds
representative of the neighborhood around the point. Using the default
configuration, the first
pass considers a square area whose dimensions are twice the resolution of
the gridded FCCS data (i.e. four times the size of a grid cell)
and centered on the input point. If this returns too high a percentage
of ignored fuelbeds (which are FCCS #0 & #900, by default), a larger
neighborhood is sampled - a square whose dimensions are six times
the grid resolution (i.e. thus 36 times the size of a grid cell).
And if this returns to much ignored, an even larger neighborhood is
sampled - a square whose dimensions are ten times
the grid resolution (i.e. thus 100 times the size of a grid cell).

The sizes and number of neighborhoods sampled can be changed
using the `sampling_radius_km` and `sampling_radius_factors`
configuration options, but the examples below are based on the
defaults.

## Examples

### One sampling

For example, using a 1km resolution grid of FCCS fuelbed data, and given
the following input,

    {
          "type": "Point",
          "coordinates": [-84.8269438083957, 32.5010839781243 ]
    }

what is actually used to look up fuelbeds is the following polygon

    {
        'type': 'MultiPolygon',
        'coordinates': [
            [
                [
                    [-84.83759501830758, 32.49207496911529],
                    [-84.83759501830758, 32.510092987133305],
                    [-84.81629259848381, 32.510092987133305],
                    [-84.81629259848381, 32.49207496911529]
                ]
            ]
        ]
    }

In this case, the initial look-up returns 75% FCCS #185 and 25% FCCS #185, and the subsequent look-up is not required.

### Two samplings

Now consider the following input, again using a 1km resolution grid of FCCS
fuelbed data

    {
          "type": "Point",
          "coordinates": [-120.4753312, 48.0786983 ]
    }

The initial lookup uses the following polygon

    {
        'coordinates': [
            [
                [
                    [-120.48877665264493, 48.06968929099099],
                    [-120.48877665264493, 48.087707309009005],
                    [-120.46188574735507, 48.087707309009005],
                    [-120.46188574735507, 48.06968929099099]
                ]
            ]
        ],
        'type': 'MultiPolygon'
    }

which returns 100% FCCS #900, which is an ignored fuelbed. So, the area is
enlarged to the following:

    {
        'coordinates': [
            [
                [
                    [-120.51566755793478, 48.051671272972975],
                    [-120.51566755793478, 48.105725327027024],
                    [-120.43499484206522, 48.105725327027024],
                    [-120.43499484206522, 48.051671272972975]
                ]
            ]
        ],
        'type': 'MultiPolygon'
    }

which returns 59.46% FCCS #52, 2.70% FCCS #60, and 37.84% FCCS #900.


## With area specified

If `area_acres` is set in the call to `FccsLookUp.look_up`, the logic described
above is followed with one exception.  The `sampling_radius_km` config setting
is ignored, and the sampling radius is instead determined based on the
specified area.

For example, consider `area_acres` set to 3954. That equals 16 km^2, which would mean a 4km x 4km square neighborhood. This translates to an
initial sampling radius of 2km. (i.e. Set the northern bounds 2km north of
the point, the eastern bounds 2km east of the point, etc.)  So, the first
sampling would use
that 4km x 4km square neighborhood. The second sampling, if required, would
use a 12km x 12km square neighborhood. And third sampling, if required, would
use a 20km x 20km square neighborhood.

## Potential Improvements

 - Use a circular neighborhood instead of square.
