import Link from "next/link";

const Navbar = () => {
  return (
    <nav className="bg-gray-900 p-4 text-white flex justify-between items-center sticky top-0 z-50">
      <Link 
        href="/" 
        className="text-xl font-bold hover:text-gray-300 transition-colors flex items-center"
      >
        � Piano Transcription
      </Link>
      <Link 
        href="/transcription" 
        className="bg-yellow-500 hover:bg-yellow-400 text-gray-900 font-semibold px-6 py-2 rounded-full transition-colors"
      >
        Transcribir
      </Link>
    </nav>
  );
};

export default Navbar;