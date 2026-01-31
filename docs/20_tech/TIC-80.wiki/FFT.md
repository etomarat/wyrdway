*This was added in version 1.2*

FFT is short for [Fast Fourier Transform](https://en.wikipedia.org/wiki/Fast_Fourier_transform), which lets us turn music into data. Its primary use in TIC-80 is Byte Jams, Byte Battles and general livecoding.

This feature is off by default; you have to launch TIC-80 with the `--fft` CLI parameter.

Usually you want to capture the loopback, i.e. whatever's playing on your computer.

On Windows, use `--fftcaptureplaybackdevices` to do so. Double-check the console output you're not accidentally capturing your microphone when running without it.

On Mac, you'll need something like [BlackHole](https://existential.audio/blackhole/), as it's not built-in.

On Linux, in theory you should have loopback by default, in practice it varies a lot.