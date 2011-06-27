/* WebP.h */

#if PY_VERSION_HEX < 0x02040000
#include <stdint.h>
#endif

typedef struct {

    /* CONFIGURATION */

    /* Quality (1-100, 0 means default) */
    int quality;

    /* INTERNAL */
    uint8_t* output_data; /* pointer to next data chunk */
    size_t output_size; /* bytes left to copy */

    uint8_t* output_buffer; /* pointer to output data buffer*/

} WEBPCONTEXT;
