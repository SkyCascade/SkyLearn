from django import forms
from accounts.models import User

from .models import (
    Program,
    Course,
    CourseAllocation,
    Upload,
    UploadVideo,
    SCORMPackage,
)


class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["title"].widget.attrs.update({
            "class": "form-control"
        })

        self.fields["summary"].widget.attrs.update({
            "class": "form-control"
        })


class CourseAddForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["title"].widget.attrs.update({
            "class": "form-control"
        })

        self.fields["code"].widget.attrs.update({
            "class": "form-control"
        })

        self.fields["credit"].widget.attrs.update({
            "class": "form-control"
        })

        self.fields["summary"].widget.attrs.update({
            "class": "form-control"
        })

        self.fields["program"].widget.attrs.update({
            "class": "form-control"
        })

        self.fields["level"].widget.attrs.update({
            "class": "form-control"
        })

        self.fields["year"].widget.attrs.update({
            "class": "form-control"
        })

        self.fields["semester"].widget.attrs.update({
            "class": "form-control"
        })


class CourseAllocationForm(forms.ModelForm):
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all().order_by("level"),
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "browser-default checkbox"}
        ),
        required=True,
    )

    lecturer = forms.ModelChoiceField(
        queryset=User.objects.filter(is_lecturer=True),
        widget=forms.Select(
            attrs={"class": "browser-default custom-select"}
        ),
        label="lecturer",
    )

    class Meta:
        model = CourseAllocation
        fields = ["lecturer", "courses"]

    def __init__(self, *args, **kwargs):
        super(CourseAllocationForm, self).__init__(*args, **kwargs)

        self.fields["lecturer"].queryset = User.objects.filter(
            is_lecturer=True
        )


class EditCourseAllocationForm(forms.ModelForm):
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all().order_by("level"),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    lecturer = forms.ModelChoiceField(
        queryset=User.objects.filter(is_lecturer=True),
        widget=forms.Select(
            attrs={"class": "browser-default custom-select"}
        ),
        label="lecturer",
    )

    class Meta:
        model = CourseAllocation
        fields = ["lecturer", "courses"]

    def __init__(self, *args, **kwargs):
        super(EditCourseAllocationForm, self).__init__(*args, **kwargs)

        self.fields["lecturer"].queryset = User.objects.filter(
            is_lecturer=True
        )


# Upload files to specific course
class UploadFormFile(forms.ModelForm):
    class Meta:
        model = Upload
        fields = (
            "title",
            "file",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["title"].widget.attrs.update({
            "class": "form-control"
        })

        self.fields["file"].widget.attrs.update({
            "class": "form-control"
        })


# Upload video / YouTube video to specific course
class UploadFormVideo(forms.ModelForm):

    class Meta:
        model = UploadVideo

        fields = (
            "title",
            "video_type",
            "video",
            "youtube_url",
            "summary",
        )

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter video title",
                }
            ),

            "video_type": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "id_video_type",
                }
            ),

            "video": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "video/*",
                    "id": "id_video",
                }
            ),

            "youtube_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://www.youtube.com/watch?v=...",
                    "id": "id_youtube_url",
                }
            ),

            "summary": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Video description (optional)",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["video"].required = False
        self.fields["youtube_url"].required = False

        self.fields["video_type"].label = "Video Type"
        self.fields["video"].label = "Upload Video File"
        self.fields["youtube_url"].label = "YouTube Video URL"

        self.fields["summary"].label = "Description"

    def clean(self):
        cleaned_data = super().clean()

        video_type = cleaned_data.get("video_type")
        video = cleaned_data.get("video")
        youtube_url = cleaned_data.get("youtube_url")

        if video_type == "file":
            if not video:
                self.add_error(
                    "video",
                    "Please select a video file."
                )

            cleaned_data["youtube_url"] = None

        elif video_type == "youtube":
            if not youtube_url:
                self.add_error(
                    "youtube_url",
                    "Please enter a YouTube video URL."
                )

            cleaned_data["video"] = None

        return cleaned_data


# Upload SCORM package to specific course
class SCORMUploadForm(forms.ModelForm):
    class Meta:
        model = SCORMPackage
        fields = (
            "title",
            "package",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["title"].widget.attrs.update({
            "class": "form-control"
        })

        self.fields["package"].widget.attrs.update({
            "class": "form-control"
        })