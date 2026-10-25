"""
Benchmark image compression algorithms and collect images for visual comparison.
"""

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
import re
from shutil import copyfile
from tempfile import TemporaryDirectory
from time import perf_counter

from PIL import Image, ImageChops, ImageStat


ImagePath = str | Path
CompressionFunction = Callable[[str, str, int | None], object]
DecompressionFunction = Callable[[str, str], object]


@dataclass(frozen=True)
class AlgorithmConfig:
    """Compression functions and settings for a benchmarked algorithm."""

    compressor: CompressionFunction
    decompressor: DecompressionFunction
    lossy: bool = False
    iteration_counts: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if self.lossy and not self.iteration_counts:
            raise ValueError("Lossy algorithms must provide iteration_counts")
        if not self.lossy and self.iteration_counts:
            raise ValueError("iteration_counts are only valid for lossy algorithms")
        if any(count < 0 for count in self.iteration_counts):
            raise ValueError("Iteration counts must be non-negative")
        if len(set(self.iteration_counts)) != len(self.iteration_counts):
            raise ValueError("Iteration counts must be unique")


@dataclass(frozen=True)
class BenchmarkResult:
    """Timing, size, and reconstruction results for one benchmark run."""

    image_path: Path
    algorithm: str
    iteration_count: int | None
    compression_seconds: float
    decompression_seconds: float
    original_size_bytes: int
    compressed_size_bytes: int
    mean_absolute_error: float
    reconstruction_path: Path | None = None

    @property
    def compression_ratio(self) -> float:
        """Return original file size divided by compressed file size."""
        return self.original_size_bytes / self.compressed_size_bytes

    @property
    def size_reduction_percent(self) -> float:
        """Return percentage size reduction relative to the original file."""
        return (
            (self.original_size_bytes - self.compressed_size_bytes)
            / self.original_size_bytes
            * 100
        )


def _algorithm_runs(config: AlgorithmConfig) -> tuple[int | None, ...]:
    return config.iteration_counts if config.lossy else (None,)


def _algorithm_label(algorithm: str, iteration_count: int | None) -> str:
    if iteration_count is None:
        return algorithm
    unit = "iteration" if iteration_count == 1 else "iterations"
    return f"{algorithm} ({iteration_count:,} {unit})"


def _reconstruction_filename(
    image_path: Path,
    algorithm: str,
    iteration_count: int | None,
) -> str:
    algorithm_name = re.sub(r"[^A-Za-z0-9._-]+", "_", algorithm).strip("_")
    suffix = "" if iteration_count is None else f"_{iteration_count}_iterations"
    return f"{image_path.stem}_{algorithm_name}{suffix}.png"


def _compress_and_decompress(
    image_path: Path,
    algorithm_name: str,
    config: AlgorithmConfig,
    iteration_count: int | None,
    compressed_path: Path,
    decoded_path: Path,
) -> tuple[float, float]:
    start = perf_counter()
    config.compressor(str(image_path), str(compressed_path), iteration_count)
    compression_seconds = perf_counter() - start

    start = perf_counter()
    config.decompressor(str(compressed_path), str(decoded_path))
    decompression_seconds = perf_counter() - start

    if not compressed_path.is_file():
        raise FileNotFoundError(
            f"{algorithm_name} did not create compressed output at {compressed_path}"
        )
    if not decoded_path.is_file():
        raise FileNotFoundError(
            f"{algorithm_name} did not create decoded output at {decoded_path}"
        )
    return compression_seconds, decompression_seconds


def _mean_absolute_error(original: Image.Image, reconstructed: Image.Image) -> float:
    original_rgb = original.convert("RGB")
    reconstructed_rgb = reconstructed.convert("RGB")
    if original_rgb.size != reconstructed_rgb.size:
        raise ValueError(
            "Decoded image dimensions do not match the original: "
            f"{reconstructed_rgb.size} != {original_rgb.size}"
        )
    return sum(ImageStat.Stat(
        ImageChops.difference(original_rgb, reconstructed_rgb)
    ).mean) / 3


def benchmark_images(
    image_paths: Iterable[ImagePath],
    algorithms: Mapping[str, AlgorithmConfig],
    reconstruction_directory: ImagePath | None = None,
) -> list[BenchmarkResult]:
    """
    Measure timing, compressed size, and reconstruction error for each run.

    Lossless algorithms run once. Lossy algorithms run once for each configured
    iteration count. Compressor callbacks receive input path, output path, and
    the iteration count (or ``None`` for a lossless run). If
    ``reconstruction_directory`` is set, decoded images are saved there.
    """
    results = []
    saved_reconstruction_directory = (
        Path(reconstruction_directory) if reconstruction_directory is not None else None
    )
    if saved_reconstruction_directory is not None:
        saved_reconstruction_directory.mkdir(parents=True, exist_ok=True)

    for image in map(Path, image_paths):
        with Image.open(image) as source_file:
            original = source_file.convert("RGB")
        original_size_bytes = image.stat().st_size

        for algorithm_name, config in algorithms.items():
            for iteration_count in _algorithm_runs(config):
                with TemporaryDirectory() as temporary_directory:
                    directory = Path(temporary_directory)
                    compressed_path = directory / "compressed.bin"
                    decoded_path = directory / "decoded.png"
                    compression_seconds, decompression_seconds = (
                        _compress_and_decompress(
                            image,
                            algorithm_name,
                            config,
                            iteration_count,
                            compressed_path,
                            decoded_path,
                        )
                    )
                    compressed_size_bytes = compressed_path.stat().st_size
                    if compressed_size_bytes == 0:
                        raise ValueError(
                            f"{algorithm_name} created an empty compressed file"
                        )

                    with Image.open(decoded_path) as decoded_file:
                        mean_absolute_error = _mean_absolute_error(
                            original, decoded_file
                        )

                    reconstruction_path = None
                    if saved_reconstruction_directory is not None:
                        reconstruction_path = saved_reconstruction_directory / (
                            _reconstruction_filename(
                                image, algorithm_name, iteration_count
                            )
                        )
                        copyfile(decoded_path, reconstruction_path)

                    results.append(BenchmarkResult(
                        image_path=image,
                        algorithm=algorithm_name,
                        iteration_count=iteration_count,
                        compression_seconds=compression_seconds,
                        decompression_seconds=decompression_seconds,
                        original_size_bytes=original_size_bytes,
                        compressed_size_bytes=compressed_size_bytes,
                        mean_absolute_error=mean_absolute_error,
                        reconstruction_path=reconstruction_path,
                    ))
    return results


def format_benchmark_results(results: Iterable[BenchmarkResult]) -> str:
    """Format benchmark results as a readable, dependency-free text table."""
    headers = (
        "Image",
        "Algorithm",
        "Original (KB)",
        "Compressed (KB)",
        "Reduction",
        "MAE",
        "Compress (s)",
        "Decompress (s)",
    )
    rows = [
        (
            result.image_path.name,
            _algorithm_label(result.algorithm, result.iteration_count),
            f"{result.original_size_bytes / 1000:,.2f}",
            f"{result.compressed_size_bytes / 1000:,.2f}",
            f"{result.size_reduction_percent:.2f}%",
            f"{result.mean_absolute_error:.2f}",
            f"{result.compression_seconds:.3f}",
            f"{result.decompression_seconds:.3f}",
        )
        for result in results
    ]
    if not rows:
        return "(no benchmark results)"

    widths = [
        max(len(header), *(len(row[index]) for row in rows))
        for index, header in enumerate(headers)
    ]
    separator = "+-" + "-+-".join("-" * width for width in widths) + "-+"

    def format_row(row: tuple[str, ...]) -> str:
        return "| " + " | ".join(
            value.ljust(widths[index]) for index, value in enumerate(row)
        ) + " |"

    return "\n".join((
        separator,
        format_row(headers),
        separator,
        *(        format_row(row) for row in rows),
        separator,
    ))