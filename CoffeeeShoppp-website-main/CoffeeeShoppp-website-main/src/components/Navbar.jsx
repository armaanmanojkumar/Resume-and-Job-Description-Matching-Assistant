import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";

const Navbar = ({ logo }) => {
  const [hidden, setHidden] = useState(false);
  let lastScroll = 0;

  useEffect(() => {
    const handleScroll = () => {
      const currentScroll = window.pageYOffset;

      if (currentScroll > lastScroll && currentScroll > 80) {
        setHidden(true);  // scroll down → hide
      } else {
        setHidden(false); // scroll up → show
      }

      lastScroll = currentScroll;
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <motion.nav
      className="fixed top-0 left-0 w-full flex items-center justify-between px-6 md:px-10 py-4 bg-transparent text-yellow-500 z-50"
      initial={{ y: 0 }}
      animate={{ y: hidden ? "-100%" : 0 }}
      transition={{ duration: 0.4, ease: "easeInOut" }}
    >
      <img src={logo} alt="Logonpm run dev -- --host
" className="w-12 md:w-14 h-auto" />
      <ul className="flex gap-6 md:gap-8 text-lg font-semibold">
        {["Home", "Story", "Shop"].map((item) => (
          <li key={item} className="hover:text-yellow-400 cursor-pointer">
            {item}
          </li>
        ))}
      </ul>
    </motion.nav>
  );
};

export default Navbar;
