import Link from "next/link";

const Navbar = () => {
  return (
    <nav className="bg-gray-900 p-4 text-white flex justify-between items-center sticky top-0 z-50">
      <Link 
        href="/" 
        className="text-xl font-bold hover:text-gray-300 transition-colors flex items-center"
      >
        🎵 AudioTranscriber
      </Link>
    </nav>
  );
};

export default Navbar;