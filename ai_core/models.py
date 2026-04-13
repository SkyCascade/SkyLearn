from django.db import models

# Create your models here.
class AIGeneration(models.Model):
    topic = models.CharField(max_length=255, null=True, blank=True)
    prompt = models.TextField(null=True, blank=True)
    
    document_file = models.FileField(upload_to="ai_docs/", null=True, blank=True)

    html_content = models.TextField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("PROCESSING", "Processing"),
            ("SUCCESS", "Success"),
            ("FAILED", "Failed"),
        ],
        default="PENDING"
    )

    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class DocumentChunk(models.Model):
    """Cached text chunk with embedding vector from an uploaded document.

    Each Upload can have many chunks. Chunks are created lazily when a
    document is first selected as RAG context for lesson generation.
    Deleting the parent Upload cascades to remove all its chunks.
    """

    upload = models.ForeignKey(
        "course.Upload",
        on_delete=models.CASCADE,
        related_name="chunks",
    )
    chunk_index = models.IntegerField(
        help_text="Zero-based position of this chunk within the document."
    )
    content = models.TextField(
        help_text="Plain text content of this chunk."
    )
    embedding = models.JSONField(
        null=True,
        blank=True,
        help_text="Embedding vector as a JSON list of floats.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["upload", "chunk_index"]
        unique_together = ["upload", "chunk_index"]

    def __str__(self) -> str:
        return f"Chunk {self.chunk_index} of Upload #{self.upload_id}"