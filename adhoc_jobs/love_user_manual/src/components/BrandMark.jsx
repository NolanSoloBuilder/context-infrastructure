export function BrandMark({ compact = false }) {
  return (
    <div className={`brand-mark ${compact ? 'brand-mark--compact' : ''}`} aria-label="关系说明书">
      <span>关系说明书</span>
      <i aria-hidden="true" />
    </div>
  );
}

export function RegistrationMark() {
  return <span className="registration-mark" aria-hidden="true" />;
}
