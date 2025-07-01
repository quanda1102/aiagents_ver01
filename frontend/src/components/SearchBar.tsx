import React from 'react';
import { SearchIcon } from 'lucide-react';
const SearchBar = () => {
  return <div className="relative">
      <input type="text" placeholder="Search..." className="w-full pl-10 pr-4 py-2 rounded-md border border-gray-300 focus:outline-none focus:border-[#007BFF] focus:ring-1 focus:ring-[#007BFF]" />
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <SearchIcon size={18} className="text-gray-400" />
      </div>
    </div>;
};
export default SearchBar;