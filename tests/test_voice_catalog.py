"""The stub catalog must never advertise a voice the real model lacks.

Regression guard for the nf_dora bug (Oct 27, 2026): the stub invented a
Nigerian voice that voices-v1.0.bin does not ship, so tests passed while the
real engine 400'd. The frozen list below is the verified content of
voices-v1.0.bin (Kokoro v1.0, model-files-v1.1 release), captured from a live
loaded engine on Oct 27, 2026. If the model file ever changes, regenerate this
snapshot from GET /v1/voices on a booted kokoro engine.
"""
import pytest

from voxserve.engines.stub import _VOICES

KOKORO_V1_0_VOICE_IDS = {
    "af_alloy", "af_aoede", "af_bella", "af_heart", "af_jessica", "af_kore",
    "af_nicole", "af_nova", "af_river", "af_sarah", "af_sky", "am_adam",
    "am_echo", "am_eric", "am_fenrir", "am_liam", "am_michael", "am_onyx",
    "am_puck", "am_santa", "bf_alice", "bf_emma", "bf_isabella", "bf_lily",
    "bm_daniel", "bm_fable", "bm_george", "bm_lewis", "ef_dora", "em_alex",
    "em_santa", "ff_siwis", "hf_alpha", "hf_beta", "hm_omega", "hm_psi",
    "if_sara", "im_nicola", "jf_alpha", "jf_gongitsune", "jf_nezumi",
    "jf_tebukuro", "jm_kumo", "pf_dora", "pm_alex", "pm_santa", "zf_xiaobei",
    "zf_xiaoni", "zf_xiaoxiao", "zf_xiaoyi", "zm_yunjian", "zm_yunxi",
    "zm_yunxia", "zm_yunyang",
}


def test_stub_catalog_is_strict_subset_of_real_voices():
    stub_ids = {v["id"] for v in _VOICES}
    assert stub_ids, "stub catalog must not be empty"
    invented = stub_ids - KOKORO_V1_0_VOICE_IDS
    assert not invented, (
        f"stub advertises voices the real model does not ship: {sorted(invented)}. "
        "Only use ids from KOKORO_V1_0_VOICE_IDS."
    )


def test_frozen_snapshot_size():
    assert len(KOKORO_V1_0_VOICE_IDS) == 54
