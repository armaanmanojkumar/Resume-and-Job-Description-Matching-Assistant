import React from "react";
import { motion } from "framer-motion";
import BgImage from "../../assets/bg-slate.png";
import Mug from "../../assets/Mug.png";
import beans from "../../assets/beans.png";
import Navbar from "../../components/Navbar";
import logo from "../../assets/logo.png";
const heroStyle = {
  backgroundImage: `url(${BgImage})`,
  backgroundSize: "cover",
  backgroundPosition: "center",
  backgroundRepeat: "no-repeat",
  height: "100vh",
  width: "100%",
};

const Hero = () => {
  return (
    <main style={heroStyle} className="w-full overflow-x-hidden">
      <Navbar logo={logo} />

      {/* HERO SECTION */}
      <section className="h-screen w-full flex items-center">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 items-center gap-6">
            
            {/* LEFT TEXT */}
            <motion.div
              className="text-center md:text-left mx-4 md:mx-0 md:ml-10 text-yellow-200 space-y-4"
              initial={{ opacity: 0, x: -80 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
            >
              <h2 className="text-3xl sm:text-4xl md:text-3xl font-semibold">Mug Story ,</h2>
              <p className="text-base sm:text-lg md:text-base opacity-80 max-w-md mx-auto md:mx-0">
                The coffee mug’s history traces back thousands of years,
                beginning when ancient civilizations used carved wood and clay
                to hold hot drinks safely...
              </p>
            </motion.div>

            {/* CENTER MUG */}
            <motion.div
              className="flex justify-center"
              initial={{ opacity: 0, scale: 0.6, rotate: -6 }}
              animate={{ opacity: 1, scale: 1, rotate: 0, y: [0, -15, 0] }}
              transition={{
                duration: 0.6,
                y: { repeat: Infinity, repeatType: "reverse", duration: 2, ease: "easeInOut" },
              }}
              whileHover={{ scale: 1.05, rotate: 2 }}
            >
              <motion.img
                src={Mug}
                alt="Coffee Mug"
                className="w-[85%] sm:w-[70%] md:w-[450px] lg:w-[500px] max-w-full drop-shadow-2xl"
              />
            </motion.div>

            {/* RIGHT TEXT */}
            <motion.div
              className="text-center md:text-right mx-4 md:mx-0 md:mr-10 text-yellow-200 space-y-3"
              initial={{ opacity: 0, x: 80 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
            >
              <h3 className="text-3xl sm:text-4xl md:text-3xl font-semibold">THE DEMO DESIGN</h3>
              <p className="text-base sm:text-lg md:text-md opacity-70">
                This is just showcase of my work
              </p>
            </motion.div>

          </div>
        </div>
      </section>

     {/* PRODUCT STORY with Background Video */}
<section className="relative h-screen w-full flex flex-col justify-center items-center px-5 overflow-hidden">

  {/* 🎬 Background Video */}
  <video
    autoPlay
    loop
    muted
    playsInline
    className="absolute top-0 left-0 w-full h-full object-cover"
  >
    <source src="/bg-video.mp4" type="video/mp4" />
  </video>

  {/* 🌓 Overlay for readability */}
  <div className="absolute inset-0 bg-black/25"></div>

  {/* 💬 Content */}
  <div className="relative z-10 text-white">
    <h2 className="text-4xl sm:text-5xl md:text-5xl font-bold mb-6 text-center">
      𝓬𝓸𝓯𝓯𝓮𝓮 𝓱𝓲𝓼𝓽𝓸𝓻𝔂
    </h2>
    <p className="max-w-xl text-center text-base sm:text-lg md:text-lg opacity-90">
      
Coffea arabica was first discovered in the highlands of Ethiopia, where legend tells of a goat herder, Kaldi, noticing his goats becoming energetic after eating wild coffee cherries. By the 15th century, coffee cultivation and trade began in Yemen, especially at the Sufi monasteries where it was used to stay awake during prayers. 
    </p>
  </div>

</section>


      {/* FEATURES */}
      <section className="relative min-h-screen w-full flex flex-col justify-center items-center px-4 sm:px-5 overflow-hidden">

  {/* 🎬 Background Video */}
  <video
    autoPlay
    loop
    muted
    playsInline
    className="absolute inset-0 w-full h-full object-cover"
  >
    <source src="/video1.mp4" type="video/mp4" />
  </video>

  {/* Overlay */}
  <div className="absolute inset-0 bg-black/20"></div>

  {/* Content Wrapper */}
  <div className="relative z-10 w-full max-w-6xl text-white text-center">

    {/* Heading */}
    <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-6 sm:mb-8">
      Fresh & Tasty
    </h2>

    {/* Grid Items */}
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 sm:gap-8">

      {["Black Coffee", "Hot Chocolate", "Cold Coffee"].map((title) => (
        <motion.div
          key={title}
          whileHover={{ scale: 1.05 }}
          className="flex flex-col items-center"
        >
          {/* Image */}
          <img
            src={beans}
            className="w-28 sm:w-36 md:w-44 mb-2 sm:mb-3"
            alt={title}
          />

          {/* Title */}
          <h3 className="text-xl sm:text-2xl font-semibold text-yellow-400">
            {title}
          </h3>

          {/* Description */}
          <p className="text-sm sm:text-base opacity-80">
            {title === "Black Coffee"
              ? "Strong, rich, coder’s fuel."
              : title === "Hot Chocolate"
              ? "Smooth & cozy."
              : "Chill but energetic."}
          </p>
        </motion.div>
      ))}

    </div>
  </div>

</section>

      {/* CTA */}
      <section className="h-screen w-full flex flex-col justify-center items-center bg-black text-yellow-400 px-4">
        <h2 className="text-4xl sm:text-5xl md:text-6xl font-extrabold">Buy Your Mug</h2>
        <p className="opacity-70 text-base sm:text-lg md:text-xl mt-2 mb-6">
          Make coffee look as good as your code
        </p>
        <motion.button
          className="bg-yellow-500 text-black px-6 py-3 sm:px-8 sm:py-4 text-lg sm:text-xl md:text-2xl font-semibold rounded-xl"
          whileTap={{ scale: 0.95 }}
        >
          Shop Now
        </motion.button>
      </section>

      {/* FOOTER */}
      <footer className="py-5 text-center bg-gray-800 text-white text-sm sm:text-base px-4">
       MADE BY - HARSHREN (7031531999)
      </footer>
    </main>
  );
};

export default Hero;
