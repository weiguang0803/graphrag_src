export default function ResultCard({ title, data, content, error, children }) {
  const cls = error ? 'result-card error' : 'result-card';
  
  // 优先用 content（App.jsx 传的），其次用 data，最后用 children
  let body;
  if (content) {
    body = content;
  } else if (data) {
    body = data.answer || data.result || data.response || JSON.stringify(data, null, 2);
  } else {
    body = children;
  }
  
  return (
    <div className={cls}>
      <h3>{title}</h3>
      <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6', color: '#333' }}>
        {body}
      </div>
    </div>
  );
}