export default function ErrorMsg({ error }) {
  if (!error) return null;
  return (
    <div className="error" role="alert">
      {error}
    </div>
  );
}
