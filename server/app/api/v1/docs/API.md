# FocusTube (v1) API Documentation

## Overview

This is the FocusTube API RESTful service that allows users to manage YouTube video links with metadata extraction capabilities. Users can register, authenticate, manage their profiles, and store video links either manually or by uploading files.

**Base URL:** `http://localhost:8000/backend/api/v1`

**API Version:** v1

## Authentication

Most endpoints require Bearer token authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## User Management Endpoints

### Register User

Creates a new user account.

**Endpoint:** `POST /register`

**Request Body:**
```json
{
  "email": "test@example.com",
  "password": "strongpassword123"
}
```

**Response:**
```json
{
  "version": "v1",
  "status": 200,
  "message": "User has been registered successfully"
}
```

**Status Codes:**
- `200` - Success
- `400` - User already exists
- `500` - Internal server error

---

### Login User

Authenticates a user and returns an access token.

**Endpoint:** `POST /login`

**Content-Type:** `application/x-www-form-urlencoded`

**Request Body:**
```
username=test@example.com&password=strongpassword123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Status Codes:**
- `200` - Success
- `401` - Invalid credentials
- `500` - Internal server error

---

### Get Current User Profile

Retrieves the authenticated user's profile information.

**Endpoint:** `GET /me`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "version": "v1",
  "status": 200,
  "id": 1,
  "email": "test@example.com",
  "profile_img": "https://example.com/profile.jpg",
  "is_oauth": false,
  "uploaded_links": 5,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-16T14:20:00Z"
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `500` - Internal server error

## Profile Image Management

### Upload Profile Image

Uploads and sets a new profile image for the authenticated user.

**Endpoint:** `POST /upload-profile-image/`

**Content-Type:** `multipart/form-data`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
- `file` (required): Image file (max 5MB)

**Response:**
```json
{
  "version": "v1",
  "status": 200,
  "file_id": "64f1b2c3d4e5f6789abc",
  "preview_url": "https://storage.example.com/preview/64f1b2c3d4e5f6789abc",
  "message": "Profile image uploaded and updated successfully"
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid file or file too large
- `401` - Unauthorized
- `500` - Server error

---

### Delete Profile Image

Removes the current user's profile image.

**Endpoint:** `DELETE /delete-profile-image`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "version": "v1",
  "status": "success",
  "message": "Profile image deleted successfully."
}
```

**Status Codes:**
- `200` - Success
- `404` - No profile image found
- `401` - Unauthorized
- `500` - Server error

## Video Link Management

### Upload Video Links Manually

Adds video links manually with automatic YouTube metadata extraction.

**Endpoint:** `POST /video-links`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "links": [
    "https://www.youtube.com/watch?v=-6LvNku2nJE",
    "https://www.youtube.com/watch?v=P7JyrhGnjhg",
    "https://www.youtube.com/shorts/9yY6A0HvDT4"
  ]
}
```

**Response:**
```json
{
  "version": "v1",
  "status": 200,
  "links": [
    {
      "url": "https://www.youtube.com/watch?v=-6LvNku2nJE",
      "metadata": {
        "id": 123,
        "title": "Sample Video Title",
        "description": "Video description...",
        "channel_title": "Channel Name",
        "thumbnail_url": "https://img.youtube.com/vi/-6LvNku2nJE/default.jpg",
        "embedded_url": "https://www.youtube.com/embed/-6LvNku2nJE",
        "uploaded_at": "2024-01-15T10:30:00Z"
      }
    }
  ],
  "source": "manual",
  "uploader": "test@example.com",
  "message": "Link has been uploaded successfully"
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `500` - Server error

---

### Upload Links from File

Extracts and uploads video links from uploaded files.

**Endpoint:** `POST /video-links/files`

**Content-Type:** `multipart/form-data`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
- `files` (required): One or more files containing video links (max 5MB each)

**Response:**
```json
{
  "version": "v1",
  "status": 200,
  "links": [
    {
      "url": "https://www.youtube.com/watch?v=example",
      "metadata": {
        "id": 124,
        "title": "Extracted Video Title",
        "description": "Video description...",
        "channel_title": "Channel Name",
        "thumbnail_url": "https://img.youtube.com/vi/example/default.jpg",
        "embedded_url": "https://www.youtube.com/embed/example",
        "uploaded_at": "2024-01-15T10:35:00Z"
      }
    }
  ],
  "source": "file",
  "uploader": "test@example.com",
  "message": "Link has been uploaded successfully"
}
```

**Status Codes:**
- `200` - Success
- `400` - File too large or invalid format
- `401` - Unauthorized
- `500` - Server error

---

### Get All Video Links

Retrieves all video links associated with the authenticated user.

**Endpoint:** `GET /videos`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "version": "v1",
  "status": 200,
  "links": [
    {
      "url": "https://www.youtube.com/watch?v=example1",
      "metadata": {
        "id": 125,
        "title": "Video Title 1",
        "description": "Description...",
        "published_at": "2023-12-01T08:00:00Z",
        "channel_title": "Channel Name",
        "thumbnail_url": "https://img.youtube.com/vi/example1/default.jpg",
        "embedded_url": "https://www.youtube.com/embed/example1",
        "uploaded_at": "2024-01-15T10:30:00Z"
      }
    }
  ],
  "source": "mixed",
  "uploader": "test@example.com",
  "message": "Response successfully generated"
}
```

**Source Values:**
- `manual` - All links added manually
- `file` - All links extracted from files
- `mixed` - Links from both sources

**Status Codes:**
- `200` - Success (returns empty array if no links found)
- `401` - Unauthorized
- `500` - Server error

---

### Delete Video Link

Removes a specific video link by its ID.

**Endpoint:** `DELETE /videos-links/{id}`

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `id` (integer): The unique identifier of the video link to delete

**Response:**
```json
{
  "version": "v1",
  "status": 200,
  "message": "Video link deleted successfully"
}
```

**Status Codes:**
- `200` - Success
- `404` - Video link not found or not owned by user
- `401` - Unauthorized

## Data Models

### VideoMetadata
```json
{
  "id": 123,
  "etag": "optional_etag",
  "title": "Video Title",
  "description": "Video description",
  "published_at": "2023-12-01T08:00:00Z",
  "channel_title": "Channel Name",
  "thumbnail_url": "https://img.youtube.com/vi/VIDEO_ID/default.jpg",
  "uploaded_at": "2024-01-15T10:30:00Z",
  "embedded_url": "https://www.youtube.com/embed/VIDEO_ID"
}
```

## Playlist Management

### Create Playlist

Creates a new playlist for the authenticated user.

**Endpoint:** `POST /playlist`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "My Favorite Videos",
  "description": "A collection of my best videos"
}
```

**Response:**
```json
{
  "version": "v1",
  "status": 201,
  "creator": "test@example.com",
  "playlist_id": 1,
  "playlist_name": "My Favorite Videos",
  "message": "Playlist created Successfully"
}
```

**Status Codes:**
- `201` - Playlist created successfully
- `401` - Unauthorized
- `500` - Internal server error

---

### Add Video to Playlist

Adds a video to a specific playlist for the authenticated user.

**Endpoint:** `POST /add-playlist`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "video_id": 51,
  "playlist_id": 1
}
```

**Response:**
```json
{
  "version": "v1",
  "status": 201,
  "creator": "test@example.com",
  "video_id": 51,
  "playlist_id": 1,
  "message": "Video successfully added to the playlist"
}
```

**Status Codes:**
- `201` - Video added to playlist
- `400` - Video already exists in playlist or bad request
- `401` - Unauthorized
- `500` - Internal server error


### VideoLinkWithMetadata
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "metadata": { /* VideoMetadata object or null */ }
}
```

### Change Playlist Visibility

Changes the visibility of a playlist for the authenticated user.

**Endpoint:** `POST /playlist-visibility`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "playlist_id": 1,
  "visibility": "public"
}
```

**Response:**
```json
{
  "version": "v1",
  "status": 202,
  "uploader": "test@example.com",
  "message": "Visibility Change Successfully to public"
}
```

**Status Codes:**
- `202` - Visibility changed successfully
- `400` - Bad request or internal server error
- `401` - Unauthorized

---

### Get All Playlists with Videos

Retrieves all playlists and their associated videos for the authenticated user.

**Endpoint:** `GET /playlists/videos`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "version": "v1",
  "status": 200,
  "playlists": [
    {
      "playlist_id": 1,
      "playlist_name": "My Favorite Videos",
      "description": "A collection of my best videos",
      "visibility": "public",
      "creator_email": "test@example.com",
      "videos": [
        {
          "id": 51,
          "title": "Sample Video Title",
          "description": "Video description...",
          "channel_title": "Channel Name",
          "thumbnail_url": "https://img.youtube.com/vi/VIDEO_ID/default.jpg",
          "uploaded_at": "2024-01-15T10:30:00Z",
          "embedded_url": "https://www.youtube.com/embed/VIDEO_ID"
        }
      ]
    }
  ],
  "message": "Fetched all playlists and their videos successfully"
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `400` - Internal server error

---

### Get All Public Playlists with Videos

Retrieves all playlists and their associated videos for the user.

**Endpoint:** `GET /playlists/videos`

**Response:**
```json
{
  "version": "v1",
  "status": 200,
  "playlists": [
    {
      "playlist_id": 1,
      "playlist_name": "My Favorite Videos",
      "description": "A collection of my best videos",
      "visibility": "public",
      "creator_email": "test@example.com",

      "videos": [
        {
          "id": 51,
          "title": "Sample Video Title",
          "description": "Video description...",
          "channel_title": "Channel Name",
          "thumbnail_url": "https://img.youtube.com/vi/VIDEO_ID/default.jpg",
          "uploaded_at": "2024-01-15T10:30:00Z",
          "embedded_url": "https://www.youtube.com/embed/VIDEO_ID"
        }
      ]
    }
  ],
  "message": "Fetched all playlists and their videos successfully"
}
```
## Video Progress Tracking

### Track Video Progress

Tracks the user's progress for a specific video.

**Endpoint:** `POST /videos/{videos_id}/progress`

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `videos_id` (integer): The unique identifier of the video

**Request Body:**
```json
{
  "last_time_watched": 120
}
```

**Response:**
```json
{
  "version": "v1",
  "is_completed": false,
  "last_time_watched": 120,
  "duration": 300,
  "completion_percentage": 40.0,
  "message": "Progress tracked set successfully"
}
```

**Status Codes:**
- `200` - Success
- `400` - Requested video not found
- `401` - Unauthorized
- `404` - Progress not found

---

### Get Video Progress

Retrieves the user's progress for a specific video.

**Endpoint:** `GET /videos/{video_id}/progress`

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `video_id` (integer): The unique identifier of the video

**Response:**
```json
{
  "version": "v1",
  "is_completed": false,
  "last_time_watched": 120,
  "duration": 300,
  "completion_percentage": 40.0,
  "message": "Progress tracked retrieved successfully"
}
```

---

### Get Video Progress

Retrieves the user's progress for a specific playlist.

**Endpoint:** `GET /playlists/{playlist_id}/progress`

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `playlist_id` (integer): The unique identifier of the video

**Response:**
```json
{
  "version": "v1",
  "status": 200,
  "playlist_id": 2,
  "playlist_name": "Tech study",
  "completion_percentage": 50.0,
  "videos_completed": 1,
  "total_videos": 2
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized
- `404` - Progress not found
- `500` - Internal server error

--- 

**Status Codes:**
- `200` - Success
- `400` - Internal server error

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error description"
}
```

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request (validation errors, file too large)
- `401` - Unauthorized (invalid or missing token)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error

## Rate Limits

- File uploads are limited to 5MB per file
- Authentication tokens have expiration times
- Duplicate links are automatically filtered out

## Notes

- YouTube metadata is automatically extracted when possible
- Links that already exist in the system are skipped during upload
- All timestamps are returned in ISO 8601 format
- The API supports both individual link uploads and batch file processing
- Profile images are stored using Appwrite storage service