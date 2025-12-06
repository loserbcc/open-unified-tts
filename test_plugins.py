#!/usr/bin/env python3
"""Test script for plugin system.

Verifies that all plugins load correctly and implement the required interface.
"""
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from plugins.base import Plugin
from plugins.ocr_plugin import OCRPlugin
from plugins.ai_director import AIDirectorPlugin
from plugins.example_plugin import ExamplePlugin, UppercasePlugin


def test_plugin(plugin: Plugin, plugin_name: str):
    """Test a plugin's basic functionality.

    Args:
        plugin: Plugin instance to test
        plugin_name: Name for display
    """
    print(f"\nTesting {plugin_name}...")

    # Test name property
    assert hasattr(plugin, 'name'), f"{plugin_name} missing 'name' property"
    print(f"  Name: {plugin.name}")

    # Test enabled property
    assert hasattr(plugin, 'enabled'), f"{plugin_name} missing 'enabled' property"
    print(f"  Enabled: {plugin.enabled}")

    # Test description
    desc = plugin.get_description()
    print(f"  Description: {desc[:80]}...")

    # Test process_text (should be pass-through when disabled)
    test_text = "Hello, world!"
    result = plugin.process_text(test_text)
    if not plugin.enabled:
        assert result == test_text, f"{plugin_name} modified text when disabled"
        print(f"  ✓ Pass-through when disabled")

    # Test UI components
    components = plugin.get_ui_components()
    print(f"  UI Components: {len(components)}")

    # Test hooks (should not raise errors)
    try:
        plugin.on_before_generate("test", "voice", "mp3")
        plugin.on_after_generate("/tmp/test.mp3", True)
        print(f"  ✓ Hooks work correctly")
    except Exception as e:
        print(f"  ✗ Hook error: {e}")
        raise

    # Test validation
    error = plugin.validate_config()
    if error:
        print(f"  Validation error: {error}")
    else:
        print(f"  ✓ Configuration valid")

    print(f"  ✓ {plugin_name} passed all tests")


def main():
    """Run all plugin tests."""
    print("=" * 70)
    print("Open Unified TTS - Plugin System Test")
    print("=" * 70)

    # Test each plugin
    plugins = [
        (OCRPlugin(), "OCR Plugin"),
        (AIDirectorPlugin(), "AI Director Plugin"),
        (ExamplePlugin(), "Example Plugin"),
        (UppercasePlugin(), "Uppercase Plugin"),
    ]

    all_passed = True
    for plugin, name in plugins:
        try:
            test_plugin(plugin, name)
        except Exception as e:
            print(f"\n✗ {name} FAILED: {e}")
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("✓ All plugins passed!")
    else:
        print("✗ Some plugins failed")
        sys.exit(1)

    # Test enabling a working plugin
    print("\nTesting plugin enable/disable...")
    example = ExamplePlugin()
    example.enabled = True
    print(f"  Enabled example plugin: {example.enabled}")

    test_input = "Hello    world   with    extra   spaces"
    test_output = example.process_text(test_input)
    print(f"  Input:  '{test_input}'")
    print(f"  Output: '{test_output}'")
    assert "  " not in test_output, "Plugin didn't clean whitespace"
    print("  ✓ Text processing works when enabled")

    example.enabled = False
    test_output2 = example.process_text(test_input)
    assert test_output2 == test_input, "Plugin modified text when disabled"
    print("  ✓ Pass-through works when disabled")

    # Test placeholder plugins can't be enabled
    print("\nTesting placeholder plugin protection...")
    ocr = OCRPlugin()
    try:
        ocr.enabled = True
        print("  ✗ OCR plugin should not be enable-able")
        all_passed = False
    except NotImplementedError as e:
        print(f"  ✓ OCR plugin correctly prevents enabling: {e}")

    print("\n" + "=" * 70)
    print("Plugin system test complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
