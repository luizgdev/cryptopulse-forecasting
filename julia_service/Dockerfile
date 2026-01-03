# 1. Base Image
FROM julia:1.10

# 2. Set working directory
WORKDIR /app

# 3. Install Packages
# We run this explicitly to ensure dependencies are baked into the image
RUN julia -e 'using Pkg; Pkg.add(["Oxygen", "HTTP", "JSON", "TimeSeries", "Statistics", "Dates", "Flux", "Zygote", "Random"]); Pkg.precompile()'

# 4. Copy Code
COPY src/ src/

# 5. Expose Port
EXPOSE 8080

# 6. Start Command
CMD ["julia", "src/api.jl"]
