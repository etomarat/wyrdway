While reading the sources for TIC-80 for a few days and working on embedding R in it as a new scripting language, I have been a little puzzled why I see the following motif so often in the api/ folder sources:

```C
/* A function declaration with `tic_mem *mem` as a formal parameter */ {
(void *) currentLangaugeVirtualMachine = ((tic_core *) mem)->currentVM;
/* ... */
}
```

The Janet, Scheme, and Python language integrations in TIC-80 each use this motif to access a void pointer to their own virtual machine. These virtual machines are each a custom type. The Janet integration, for example, casts the void pointer to a `JanetTable *`, which then means to the overall system (and to the embedded Janet language interpreter) that a very important object of type `JanetTable` is located at the address of the third member (`currentVM`) of the struct `core`. `core` seems to always be a `tic_core *`, so the arrow operator is used to dereference the pointer to obtain the third struct member address (that of `currentVM`).

Not all embedded languages work this way; some use `extern` variables to define global state which is available globally.

***

https://github.com/nesbox/TIC-80/blob/0e34eaaa50bfdefa546988edc0c8efa1bf280130/src/core/core.h#L171-L213
```C
typedef struct
{
    tic_mem memory; // it should be first
    tic80_pixel_color_format screen_format;


    void* currentVM;
    const tic_script* currentScript;


    struct
    {
        struct blip_t* left;
        struct blip_t* right;
    } blip;


    s32 samplerate;
    tic_tick_data* data;
    tic_core_state_data state;


    struct
    {
        tic_core_state_data state;
        tic_ram ram;
        u8 input;


        struct
        {
            u64 start;
            u64 paused;
        } time;
    } pause;


    struct
    {
    #define API_FUNC_DEF(name, _, __, ___, ____, _____, ret, ...) ret (*name)(__VA_ARGS__);
        TIC_API_LIST(API_FUNC_DEF)
    #undef  API_FUNC_DEF


#if defined BUILD_DEPRECATED
        void (*textri)(tic_mem* tic, float x1, float y1, float x2, float y2, float x3, float y3, float u1, float v1, float u2, float v2, float u3, float v3, bool use_map, u8* colors, s32 count);
#endif
    } api;


} tic_core;
```

***

My hand-written note on this subject begins with a *very* rough visualization of the `tic_core` struct typedef (the types of the members are encircled and the names listed next to the types). The remainder of the note (a single loose leaf) ends with the following paragraph, which inspired me to write this Wiki page for others enlightenment and reference, because this was a topic I needed to spend much time with given this was my first "real, major" C project (I've only written small toy programs otherwise).

> Type-casting `tic_mem *` "mem" to `tic_core *` informs the system that whatever the address of this "mem" is there is also there, colocated at the same address, a struct of type `tic_core`. The other members of the struct can be found through dereferencing. `((tic_core *) mem)->currentVM` will return a pointer (of the void type) to the "current [langauge] virtual machine."