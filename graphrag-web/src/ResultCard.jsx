export default function ResultCard({ title, data, error, children }) {
  const cls = error ? 'result-card error' : 'result-card';
  let body = children;
  if (data) {
    // 兼容后端返回 { answer: "..." } 或 { result: "..." } 或直接字符串
    body = data.answer || data.result || data.response || JSON.stringify(data, null, 2);
  }
  return (
    <div className={cls}>
      <h3>{title}</h3>
      <div>{body}</div>
    </div>
  );
}
