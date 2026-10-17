#pragma once

// Component gain only. User master/music preferences still multiply once in the bus.
// The selected immutable PCM has peak0.5, so max1.6 leaves music peak at0.8.
namespace ParisTutorialMusicPolicy {
enum class EContext { Opening, Pause, Training, Approach, Combat, Secured };
constexpr float Target(EContext Context,bool Speaking=false){
    const float Gain=Context==EContext::Opening?1.60f:
        Context==EContext::Pause?1.10f:
        Context==EContext::Training?.55f:
        Context==EContext::Approach?.80f:
        Context==EContext::Combat?1.15f:.45f;
    return Gain*(Speaking?.22f:1.f);
}
}
