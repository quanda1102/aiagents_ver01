# Class Selection Page Documentation

## 📋 **Overview**

The Class Selection page (`/pages/class-selection.html`) allows students to assign themselves to specific AI classes by updating their `class_name` field in the database.

## 🎯 **Features**

### ✅ **Class Display**
- Shows 12 AI classes: "Lớp trí tuệ nhân tạo lớp 1" through "Lớp trí tuệ nhân tạo lớp 12"
- Each class maps to codes: AI-01, AI-02, AI-03, ... AI-12
- Visual grid layout with hover effects and selection states

### ✅ **Current Class Info**
- Displays user's current class at the top (if assigned)
- Shows full class name (e.g., "Lớp trí tuệ nhân tạo lớp 3")
- Highlights currently selected class card

### ✅ **Interactive Selection**
- Click any class card to assign yourself to that class
- Loading states during API calls
- Visual feedback with success/error messages
- Prevents duplicate selections

## 🔌 **API Integration**

### **Endpoint**: `PUT /api/v1/auth/me/class-name`

### **Request Format**:
```javascript
{
  "class_name": "AI-03"  // Class code (AI-01 through AI-12)
}
```

### **Headers**:
```javascript
{
  "Content-Type": "application/json",
  "Authorization": "Bearer [access_token]"
}
```

### **Response**:
```javascript
{
  "detail": "Class name updated successfully",
  "class_name": "AI-03"
}
```

## 🎨 **UI Components**

### **Class Cards**
- **Default State**: White background, blue hover effect
- **Selected State**: Green border, light green background
- **Loading State**: Dimmed opacity, disabled clicks
- **Content**: Class icon, title, and code

### **Messages**
- **Success**: Green background, auto-hide after 5 seconds
- **Error**: Red background, shows error details
- **Info**: Blue background for informational messages

### **Current Class Display**
- Purple gradient header showing current assignment
- Only visible if user has a class assigned

## 📱 **User Experience**

### **Flow**:
1. **Page Load**: Fetches current user info and class assignment
2. **Display**: Shows all 12 classes with current selection highlighted
3. **Selection**: User clicks desired class card
4. **Update**: API call updates database with new class_name
5. **Feedback**: Success message and UI updates

### **Error Handling**:
- Authentication failures
- Network connection issues
- API server errors
- Duplicate selection attempts

## 🔐 **Security & Authentication**

- **Login Required**: Uses `requireAuth()` to ensure user is logged in
- **Token Validation**: Includes Bearer token in API requests
- **Current User**: Fetches user data from `/api/v1/auth/me`
- **Error Handling**: Redirects to login if authentication fails

## 🗂 **Class Mapping**

| Display Name | Class Code | Database Value |
|--------------|------------|----------------|
| Lớp trí tuệ nhân tạo lớp 1 | AI-01 | AI-01 |
| Lớp trí tuệ nhân tạo lớp 2 | AI-02 | AI-02 |
| Lớp trí tuệ nhân tạo lớp 3 | AI-03 | AI-03 |
| ... | ... | ... |
| Lớp trí tuệ nhân tạo lớp 12 | AI-12 | AI-12 |

## 🛠 **Technical Implementation**

### **Key Functions**:

```javascript
// Load and display current user info
loadCurrentUser()

// Generate the grid of class cards
generateClassCards()

// Handle class selection and API call
selectClass(classCode, cardElement)

// Display success/error messages
showMessage(message, type)
```

### **Data Structure**:
```javascript
const classes = [
  { id: 1, title: 'Lớp trí tuệ nhân tạo lớp 1', code: 'AI-01' },
  { id: 2, title: 'Lớp trí tuệ nhân tạo lớp 2', code: 'AI-02' },
  // ... more classes
];
```

## 🔗 **Navigation Integration**

The page is accessible via:
- **Sidebar**: Under "Quản lý" → "Chọn lớp học"
- **Direct URL**: `/pages/class-selection.html`
- **Breadcrumb**: Dashboard → Chọn lớp học

## 📋 **Usage Examples**

### **For Students**:
1. Login to the system
2. Navigate to "Quản lý" → "Chọn lớp học"
3. See current class assignment (if any)
4. Click desired class card
5. Confirm successful assignment

### **For Teachers/Admins**:
- Can view student assignments through user management
- Class assignments appear in user profiles
- Useful for organizing students by grade level

## 🚀 **Deployment**

### **Files Created**:
- ✅ `/frontend/files/src/pages/class-selection.html` - Main page
- ✅ `/frontend/files/src/pages/CLASS-SELECTION-README.md` - This documentation

### **Dependencies**:
- ✅ `auth.js` - Authentication functions
- ✅ Existing CSS framework and icons
- ✅ Backend API endpoint `/api/v1/auth/me/class-name`

### **Testing**:
1. **Login Test**: Ensure authentication works
2. **API Test**: Verify class updates in database
3. **UI Test**: Check responsive design and interactions
4. **Error Test**: Test network failures and invalid requests

## 📊 **Benefits**

- **Self-Service**: Students can assign themselves without admin intervention
- **Visual Feedback**: Clear indication of current and available classes
- **Data Integrity**: Validates selections and provides error handling
- **User Experience**: Intuitive interface matching existing design system 