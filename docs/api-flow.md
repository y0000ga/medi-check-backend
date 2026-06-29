# API 流程

## 分層流程

1. Route 層接收請求
2. Route 層組裝 payload
3. Service 層進行驗證與商業邏輯處理
4. Repository 層讀寫資料庫
5. Service 層組裝回應 DTO
6. Route 層回傳 API response

## Auth 流程

支援的端點：

- `POST /auth/sign-up`
- `POST /auth/sign-in`
- `POST /auth/refresh`
- `POST /auth/logout`
- `POST /auth/forgot-password`（stub，尚未實作）
- `POST /auth/reset-password`（stub，尚未實作）

### Token 模型

- `access_token` 是短效 token，供一般 API 透過 `Authorization: Bearer <access_token>` 使用
- `refresh_token` 是長效 token，只會在 `refresh` 與 `logout` 時透過 request body 傳入
- refresh token 會以雜湊值儲存在資料庫的 `user_sessions` 表
- `refresh` 時會進行 refresh token rotation

### 註冊

1. 建立 `users`
2. 建立關聯的 `patients`
3. 建立 `user_sessions`
4. 在 response body 回傳 `user_id`、`access_token`、`refresh_token`

### 登入

1. 依 email 找出使用者
2. 驗證密碼
3. 建立 `user_sessions`
4. 在 response body 回傳 `user_id`、`access_token`、`refresh_token`

### 更新 Token

Request body：

```json
{
  "refresh_token": "string"
}
```

流程：

1. 解析並驗證 refresh token
2. 依 token id 找到對應的 `user_sessions` 資料
3. 驗證 token hash、過期時間與撤銷狀態
4. 將目前 session 標記為 revoked
5. 建立新的 session 與新的 refresh token
6. 回傳新的 `access_token` 與 `refresh_token`

### 登出

Request body：

```json
{
  "refresh_token": "string"
}
```

流程：

1. 解析 refresh token
2. 找到對應的 `user_sessions` 資料
3. 若仍有效則標記為 revoked
4. 即使 token 已過期或已撤銷，也直接回傳成功，避免前端卡住

## 主要資源流程

### Users

支援的端點：

- `GET /users/me`
- `PATCH /users/me`

### Patients

支援的端點：

- `GET /patients`
- `GET /patients/options`
- `POST /patients`
- `GET /patients/{patient_id}`
- `PUT /patients/{patient_id}`

### Medications

支援的端點：

- `GET /medications`
- `GET /patients/{patient_id}/medications`
- `POST /patients/{patient_id}/medications`
- `GET /medications/{medication_id}`
- `PATCH /medications/{medication_id}`
- `DELETE /medications/{medication_id}`

### Schedules

支援的端點：

- `GET /schedules`
- `GET /schedules/{schedule_id}`
- `POST /medications/{medication_id}/schedules`
- `PATCH /schedules/{schedule_id}`
- `DELETE /schedules/{schedule_id}`
- `GET /schedule-matches`

### Histories

支援的端點：

- `GET /histories`
- `GET /histories/{history_id}`
- `POST /histories/quick-check`
- `PATCH /histories/{history_id}`

### Care Invitations

支援的端點：

- `GET /care-invitations`
- `POST /care-invitations/me/caregiver`
- `POST /care-invitations/me/patient`
- `POST /care-invitations/{invitation_id}/revoke`
- `POST /care-invitations/{invitation_id}/decline`
- `POST /care-invitations/{invitation_id}/accept`

### Care Relationships

支援的端點：

- `GET /care-relationships`

### App Config

支援的端點：

- `GET /app-config/validation`

## 注意事項

- Web 與 mobile 共用相同的 token 合約，透過 response / body 欄位傳遞
- Mobile client 應將 `access_token` 與 `refresh_token` 存放於安全儲存區
- mobile flow 不依賴 cookie 處理 refresh token
