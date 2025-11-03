"""Tests for image generation functionality."""

import pytest
from unittest.mock import patch, MagicMock, Mock
from pathlib import Path
from PIL import Image
from src.image_generator import ImageGenerator, generate_cartoon_image_from_data


class TestImageGenerator:
    """Tests for ImageGenerator class."""

    @patch('src.image_generator.get_api_key')
    @patch('src.image_generator.genai.configure')
    @patch('src.image_generator.genai.GenerativeModel')
    def test_init_with_api_key(self, mock_model, mock_configure, mock_get_key):
        """Test ImageGenerator initialization with API key."""
        generator = ImageGenerator(api_key="test-key")
        assert generator.api_key == "test-key"
        mock_configure.assert_called_once_with(api_key="test-key")

    @patch('src.image_generator.get_api_key')
    @patch('src.image_generator.genai.configure')
    @patch('src.image_generator.genai.GenerativeModel')
    def test_init_without_api_key(self, mock_model, mock_configure, mock_get_key):
        """Test ImageGenerator initialization without API key."""
        mock_get_key.return_value = "fetched-key"
        generator = ImageGenerator()
        assert generator.api_key == "fetched-key"
        mock_configure.assert_called_once_with(api_key="fetched-key")

    @patch('src.image_generator.get_api_key')
    @patch('src.image_generator.genai.configure')
    @patch('src.image_generator.genai.GenerativeModel')
    def test_build_image_prompt(self, mock_model, mock_configure, mock_get_key):
        """Test image prompt building."""
        mock_get_key.return_value = "test-key"

        generator = ImageGenerator()
        prompt = generator._build_image_prompt(
            "Test Cartoon",
            "A funny premise",
            "Melbourne",
            "newspaper comic strip"
        )

        assert "Test Cartoon" in prompt
        assert "A funny premise" in prompt
        assert "Melbourne" in prompt
        assert "newspaper comic strip" in prompt
        assert "Art style requirements" in prompt

    @patch('src.image_generator.get_api_key')
    @patch('src.image_generator.genai.configure')
    @patch('src.image_generator.genai.GenerativeModel')
    def test_create_placeholder_image(self, mock_model, mock_configure, mock_get_key):
        """Test placeholder image creation."""
        mock_get_key.return_value = "test-key"

        generator = ImageGenerator()
        image = generator.create_placeholder_image(
            "Test Title",
            "This is a test premise for a cartoon",
            800,
            600
        )

        assert isinstance(image, Image.Image)
        assert image.size == (800, 600)
        assert image.mode == 'RGB'

    @patch('src.image_generator.get_api_key')
    @patch('src.image_generator.genai.configure')
    @patch('src.image_generator.genai.GenerativeModel')
    def test_create_placeholder_image_default_size(self, mock_model, mock_configure, mock_get_key):
        """Test placeholder image with default dimensions."""
        mock_get_key.return_value = "test-key"

        generator = ImageGenerator()
        image = generator.create_placeholder_image("Title", "Premise")

        assert isinstance(image, Image.Image)
        assert image.size == (800, 600)

    @patch('src.image_generator.get_api_key')
    @patch('src.image_generator.genai.configure')
    @patch('src.image_generator.genai.GenerativeModel')
    def test_save_image(self, mock_model, mock_configure, mock_get_key, tmp_path):
        """Test image saving."""
        mock_get_key.return_value = "test-key"

        generator = ImageGenerator()
        image = Image.new('RGB', (100, 100), color='white')

        cartoon_data = {
            'location': 'Melbourne, Australia',
            'winner': 'Test Cartoon'
        }

        with patch('src.image_generator.Path') as mock_path_class:
            mock_path = MagicMock()
            mock_path.__truediv__ = lambda self, other: tmp_path / other
            mock_path.mkdir = MagicMock()
            mock_path_class.return_value = mock_path

            # Create actual file in tmp_path
            output_path = tmp_path / "test.png"
            image.save(output_path)

            result = generator.save_image(image, cartoon_data, tmp_path)

            assert result is not None
            assert isinstance(result, Path)

    @patch('src.image_generator.get_api_key')
    @patch('src.image_generator.genai.configure')
    @patch('src.image_generator.genai.GenerativeModel')
    def test_generate_cartoon_image_no_image_support(
        self,
        mock_model_class,
        mock_configure,
        mock_get_key
    ):
        """Test cartoon generation when image generation not supported."""
        mock_get_key.return_value = "test-key"

        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Image description"
        # No image attribute
        del mock_response.image
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        generator = ImageGenerator()
        result = generator.generate_cartoon_image(
            "Test Title",
            "Test Premise",
            "Test Location"
        )

        assert result is None

    @patch('src.image_generator.get_api_key')
    @patch('src.image_generator.genai.configure')
    @patch('src.image_generator.genai.GenerativeModel')
    def test_generate_cartoon_image_error(
        self,
        mock_model_class,
        mock_configure,
        mock_get_key
    ):
        """Test cartoon generation with error."""
        mock_get_key.return_value = "test-key"

        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_model_class.return_value = mock_model

        generator = ImageGenerator()
        result = generator.generate_cartoon_image(
            "Test Title",
            "Test Premise",
            "Test Location"
        )

        assert result is None

    @patch.object(ImageGenerator, 'create_placeholder_image')
    @patch.object(ImageGenerator, 'save_image')
    @patch('src.image_generator.get_api_key')
    @patch('src.image_generator.genai.configure')
    @patch('src.image_generator.genai.GenerativeModel')
    def test_generate_and_save_with_placeholder(
        self,
        mock_model,
        mock_configure,
        mock_get_key,
        mock_save,
        mock_placeholder
    ):
        """Test generate_and_save with placeholder mode."""
        mock_get_key.return_value = "test-key"

        cartoon_data = {
            'topic': 'Test Topic',
            'location': 'Melbourne, Australia',
            'ideas': [
                {
                    'title': 'Winner Cartoon',
                    'premise': 'Funny premise',
                    'why_funny': 'Very funny'
                }
            ],
            'ranking': ['Winner Cartoon'],
            'winner': 'Winner Cartoon'
        }

        mock_image = MagicMock(spec=Image.Image)
        mock_placeholder.return_value = mock_image
        mock_save.return_value = Path('/fake/path/image.png')

        generator = ImageGenerator()
        result = generator.generate_and_save(cartoon_data, use_placeholder=True)

        assert result == Path('/fake/path/image.png')
        mock_placeholder.assert_called_once_with('Winner Cartoon', 'Funny premise')
        mock_save.assert_called_once()

    @patch.object(ImageGenerator, 'generate_cartoon_image')
    @patch.object(ImageGenerator, 'create_placeholder_image')
    @patch.object(ImageGenerator, 'save_image')
    @patch('src.image_generator.get_api_key')
    @patch('src.image_generator.genai.configure')
    @patch('src.image_generator.genai.GenerativeModel')
    def test_generate_and_save_no_winner_found(
        self,
        mock_model,
        mock_configure,
        mock_get_key,
        mock_save,
        mock_placeholder,
        mock_generate
    ):
        """Test generate_and_save when winner not found in ideas."""
        mock_get_key.return_value = "test-key"

        cartoon_data = {
            'topic': 'Test Topic',
            'location': 'Melbourne, Australia',
            'ideas': [
                {
                    'title': 'Other Cartoon',
                    'premise': 'Different premise',
                    'why_funny': 'Also funny'
                }
            ],
            'ranking': ['Winner Cartoon'],
            'winner': 'Winner Cartoon'  # Not in ideas
        }

        generator = ImageGenerator()
        result = generator.generate_and_save(cartoon_data)

        assert result is None

    @patch.object(ImageGenerator, 'generate_cartoon_image')
    @patch.object(ImageGenerator, 'create_placeholder_image')
    @patch.object(ImageGenerator, 'save_image')
    @patch('src.image_generator.get_api_key')
    @patch('src.image_generator.genai.configure')
    @patch('src.image_generator.genai.GenerativeModel')
    def test_generate_and_save_fallback_to_placeholder(
        self,
        mock_model,
        mock_configure,
        mock_get_key,
        mock_save,
        mock_placeholder,
        mock_generate
    ):
        """Test generate_and_save falls back to placeholder when generation fails."""
        mock_get_key.return_value = "test-key"

        cartoon_data = {
            'topic': 'Test Topic',
            'location': 'Melbourne, Australia',
            'ideas': [
                {
                    'title': 'Winner Cartoon',
                    'premise': 'Funny premise',
                    'why_funny': 'Very funny'
                }
            ],
            'ranking': ['Winner Cartoon'],
            'winner': 'Winner Cartoon'
        }

        mock_generate.return_value = None  # Generation fails
        mock_image = MagicMock(spec=Image.Image)
        mock_placeholder.return_value = mock_image
        mock_save.return_value = Path('/fake/path/image.png')

        generator = ImageGenerator()
        result = generator.generate_and_save(cartoon_data, use_placeholder=False)

        assert result == Path('/fake/path/image.png')
        mock_generate.assert_called_once()
        mock_placeholder.assert_called_once()


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @patch('src.image_generator.ImageGenerator')
    def test_generate_cartoon_image_from_data(self, mock_generator_class):
        """Test generate_cartoon_image_from_data convenience function."""
        mock_generator = MagicMock()
        mock_generator.generate_and_save.return_value = Path('/fake/path/image.png')
        mock_generator_class.return_value = mock_generator

        cartoon_data = {
            'topic': 'Test',
            'location': 'Test Location',
            'ideas': [],
            'winner': 'Test'
        }

        result = generate_cartoon_image_from_data(
            cartoon_data,
            api_key="test-key",
            use_placeholder=True
        )

        assert result == Path('/fake/path/image.png')
        mock_generator_class.assert_called_once_with(api_key="test-key")
        mock_generator.generate_and_save.assert_called_once_with(
            cartoon_data,
            True
        )

    @patch('src.image_generator.ImageGenerator')
    def test_generate_cartoon_image_from_data_no_placeholder(self, mock_generator_class):
        """Test generating image without placeholder mode."""
        mock_generator = MagicMock()
        mock_generator.generate_and_save.return_value = Path('/fake/path/image.png')
        mock_generator_class.return_value = mock_generator

        cartoon_data = {'ideas': [], 'winner': 'Test'}

        result = generate_cartoon_image_from_data(cartoon_data)

        mock_generator.generate_and_save.assert_called_once_with(
            cartoon_data,
            False
        )
