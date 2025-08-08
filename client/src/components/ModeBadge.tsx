export default function ModeBadge({ mode }: { mode: Modes }) {
  let modeBgColor = "";

  switch (mode) {
    case "idle":
      modeBgColor = "bg-yellow-500";
      break;
    case "speaking":
      modeBgColor = "bg-green-500";
      break;
    case "thinking":
      modeBgColor = "bg-blue-500";
      break;
    case "listening":
      modeBgColor = "bg-orange-500";
      break;
    default:
      modeBgColor = "bg-gray-500";
  }

  return (
    <span className="absolute top-2 right-2 flex items-center gap-2
                text-white text-sm font-medium bg-white/10 backdrop-blur-md
                rounded-full px-4 py-2 border border-white/20 shadow-xl
                cursor-pointer hover:bg-white/20 hover:border-white/30
                transition-all duration-200">
      <span className={`inline-block w-3 h-3 rounded-full ${modeBgColor}`} />
      <span>{mode.toUpperCase()}</span>
    </span>
  );
}
