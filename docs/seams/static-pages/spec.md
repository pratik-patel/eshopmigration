# Seam Specification: Static Pages

**Seam ID**: `static-pages`
**Priority**: 4 (Low)
**Complexity**: Low
**Status**: Pending Discovery

---

## Purpose

About and Contact pages with static content and no dynamic functionality.

## Scope

### In-Scope
- About page content and layout
- Contact page content and layout
- Integration with site master page/layout
- Styling preservation

### Out-of-Scope
- Contact form functionality (not in legacy)
- Dynamic content loading
- User authentication/personalization

## Legacy Implementation

### About Page
**Page**: `About.aspx` + `About.aspx.cs`
**Route**: `/About`
**Master Page**: `Site.Master`
**Content**: Static text about the application

### Contact Page
**Page**: `Contact.aspx` + `Contact.aspx.cs`
**Route**: `/Contact`
**Master Page**: `Site.Master`
**Content**: Static contact information

## Dependencies

### Services
None - these are pure static content pages

### Models
None

### Cross-Seam Dependencies
- Uses **layout** (Site.Master)

## UI Layout

### About Page
- Heading: "Your application description page."
- Paragraph with placeholder text
- Standard site layout (header, footer, navigation)

### Contact Page
- Heading: "Contact"
- Address information section
- Phone/email information section
- Support information section

## Business Rules

None - static content only

## Migration Target

### Backend
**No backend routes needed** - these are frontend-only pages

Alternatively, if content management desired:
- `GET /api/static-content/about` (returns markdown or HTML)
- `GET /api/static-content/contact` (returns markdown or HTML)

### Frontend

**Routes**:
- `/about` → `AboutPage.tsx`
- `/contact` → `ContactPage.tsx`

**Components**:
- `AboutPage` - static about content
- `ContactPage` - static contact content

**Implementation**:
```tsx
// AboutPage.tsx
export function AboutPage() {
  return (
    <div className="container">
      <h1>About eShop</h1>
      <p>Your application description page.</p>
      <p>
        Use this area to provide additional information about your application.
      </p>
    </div>
  );
}

// ContactPage.tsx
export function ContactPage() {
  return (
    <div className="container">
      <h1>Contact</h1>
      <address>
        One Microsoft Way<br />
        Redmond, WA 98052-6399<br />
        <abbr title="Phone">P:</abbr> 425.555.0100
      </address>

      <address>
        <strong>Support:</strong> <a href="mailto:Support@example.com">Support@example.com</a><br />
        <strong>Marketing:</strong> <a href="mailto:Marketing@example.com">Marketing@example.com</a>
      </address>
    </div>
  );
}
```

## Success Criteria

- [ ] About page displays with correct content
- [ ] Contact page displays with correct content
- [ ] Pages integrate with site layout (header/nav/footer)
- [ ] Styling matches legacy pages
- [ ] Navigation links work

## Test Scenarios

1. **Navigate to About page**
   - Click "About" link in navigation
   - Verify page displays
   - Verify content matches legacy

2. **Navigate to Contact page**
   - Click "Contact" link in navigation
   - Verify page displays
   - Verify content matches legacy

3. **Navigation back to home**
   - From About/Contact, click logo or home link
   - Verify navigates back to catalog list

## Notes

- Lowest priority seam - can be migrated last
- Simple implementation - good for testing layout integration
- Content can be extracted from legacy .aspx files
- Consider making content editable via CMS in future (post-migration enhancement)
