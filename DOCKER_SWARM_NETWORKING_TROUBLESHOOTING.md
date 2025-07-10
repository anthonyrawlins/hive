# Docker Swarm Networking Troubleshooting Guide

**Date**: July 8, 2025  
**Context**: Comprehensive analysis of Docker Swarm routing mesh and Traefik integration issues  
**Status**: Diagnostic guide based on official documentation and community findings  

---

## 🎯 **Executive Summary**

This guide provides a comprehensive troubleshooting framework for Docker Swarm networking issues, specifically focusing on routing mesh failures and Traefik integration problems. Based on extensive analysis of official Docker and Traefik documentation, community forums, and practical testing, this guide identifies the most common root causes and provides systematic diagnostic procedures.

## 📋 **Problem Categories**

### **1. Routing Mesh Failures**
- **Symptom**: Published service ports not accessible via `localhost:port`
- **Impact**: Services only accessible via direct node IP addresses
- **Root Cause**: Infrastructure-level networking issues

### **2. Traefik Integration Issues**
- **Symptom**: HTTPS endpoints return "Bad Gateway" (502)
- **Impact**: External access to services fails despite internal health
- **Root Cause**: Service discovery and overlay network connectivity

### **3. Selective Service Failures**
- **Symptom**: Some services work via routing mesh while others fail
- **Impact**: Inconsistent service availability
- **Root Cause**: Service-specific configuration or placement issues

---

## 🔍 **Diagnostic Framework**

### **Phase 1: Infrastructure Validation**

#### **1.1 Required Port Connectivity**
Docker Swarm requires specific ports to be open between ALL nodes:

```bash
# Test cluster management port
nc -zv <node-ip> 2377

# Test container network discovery (TCP/UDP)
nc -zv <node-ip> 7946
nc -zuv <node-ip> 7946

# Test overlay network data path
nc -zuv <node-ip> 4789
```

**Expected Result**: All ports should be reachable from all nodes

#### **1.2 Kernel Module Verification**
Docker Swarm overlay networks require specific kernel modules:

```bash
# Check required kernel modules
lsmod | grep -E "(bridge|ip_tables|nf_nat|overlay|br_netfilter)"

# Load missing modules if needed
sudo modprobe bridge
sudo modprobe ip_tables
sudo modprobe nf_nat
sudo modprobe overlay
sudo modprobe br_netfilter
```

**Expected Result**: All modules should be loaded and active

#### **1.3 Firewall Configuration**
Ensure permissive rules for internal cluster communication:

```bash
# Add comprehensive internal subnet rules
sudo ufw allow from 192.168.1.0/24 to any
sudo ufw allow to 192.168.1.0/24 from any

# Add specific Docker Swarm ports
sudo ufw allow 2377/tcp
sudo ufw allow 7946
sudo ufw allow 4789/udp
```

**Expected Result**: All cluster traffic should be permitted

### **Phase 2: Docker Swarm Health Assessment**

#### **2.1 Cluster Status Validation**
```bash
# Check overall cluster health
docker node ls

# Verify node addresses
docker node inspect <node-name> --format '{{.Status.Addr}}'

# Check swarm configuration
docker system info | grep -A 10 "Swarm"
```

**Expected Result**: All nodes should be "Ready" with proper IP addresses

#### **2.2 Ingress Network Inspection**
```bash
# Examine ingress network configuration
docker network inspect ingress

# Check ingress network containers
docker network inspect ingress --format '{{json .Containers}}' | python3 -m json.tool

# Verify ingress network subnet
docker network inspect ingress --format '{{json .IPAM.Config}}'
```

**Expected Result**: Ingress network should contain active service containers

#### **2.3 Service Port Publishing Verification**
```bash
# Check service port configuration
docker service inspect <service-name> --format '{{json .Endpoint.Ports}}'

# Verify service placement
docker service ps <service-name>

# Check service labels (for Traefik)
docker service inspect <service-name> --format '{{json .Spec.Labels}}'
```

**Expected Result**: Ports should be properly published with "ingress" mode

### **Phase 3: Service-Specific Diagnostics**

#### **3.1 Internal Service Connectivity**
```bash
# Test service-to-service communication
docker run --rm --network <network-name> alpine/curl -s http://<service-name>:<port>/health

# Check DNS resolution
docker run --rm --network <network-name> alpine/curl nslookup <service-name>

# Test direct container connectivity
docker run --rm --network <network-name> alpine/curl -s http://<container-ip>:<port>/health
```

**Expected Result**: Services should be reachable via service names

#### **3.2 Routing Mesh Validation**
```bash
# Test routing mesh functionality
curl -s http://localhost:<published-port>/ --connect-timeout 5

# Test from different nodes
ssh <node-ip> "curl -s http://localhost:<published-port>/ --connect-timeout 5"

# Check port binding status
ss -tulpn | grep :<published-port>
```

**Expected Result**: Services should be accessible from all nodes

#### **3.3 Traefik Integration Assessment**
```bash
# Test Traefik service discovery
curl -s https://traefik.home.deepblack.cloud/api/rawdata

# Check Traefik service status
docker service logs <traefik-service> --tail 20

# Verify certificate provisioning
curl -I https://<service-domain>/
```

**Expected Result**: Traefik should discover services and provision certificates

---

## 🛠️ **Common Resolution Strategies**

### **Strategy 1: Infrastructure Fixes**

#### **Firewall Resolution**
```bash
# Apply comprehensive firewall rules
sudo ufw allow from 192.168.1.0/24 to any
sudo ufw allow to 192.168.1.0/24 from any
sudo ufw allow 2377/tcp
sudo ufw allow 7946
sudo ufw allow 4789/udp
```

#### **Kernel Module Resolution**
```bash
# Load all required modules
sudo modprobe bridge ip_tables nf_nat overlay br_netfilter

# Make persistent (add to /etc/modules)
echo -e "bridge\nip_tables\nnf_nat\noverlay\nbr_netfilter" | sudo tee -a /etc/modules
```

#### **Docker Daemon Restart**
```bash
# Restart Docker daemon to reset networking
sudo systemctl restart docker

# Wait for swarm reconvergence
sleep 60

# Verify cluster health
docker node ls
```

### **Strategy 2: Configuration Fixes**

#### **Service Placement Optimization**
```yaml
# Remove restrictive placement constraints
deploy:
  placement:
    constraints: []  # Remove manager-only constraints
```

#### **Network Configuration**
```yaml
# Ensure proper network configuration
networks:
  - hive-network    # Internal communication
  - tengig          # Traefik integration
```

#### **Port Mapping Standardization**
```yaml
# Add explicit port mappings for debugging
ports:
  - "<external-port>:<internal-port>"
```

### **Strategy 3: Advanced Troubleshooting**

#### **Data Path Port Change**
```bash
# If port 4789 conflicts, change data path port
docker swarm init --data-path-port=4790
```

#### **Service Force Restart**
```bash
# Force service restart to reset networking
docker service update --force <service-name>
```

#### **Ingress Network Recreation**
```bash
# Nuclear option: recreate ingress network
docker network rm ingress
docker network create \
  --driver overlay \
  --ingress \
  --subnet=10.0.0.0/24 \
  --gateway=10.0.0.1 \
  --opt com.docker.network.driver.mtu=1200 \
  ingress
```

---

## 📊 **Diagnostic Checklist**

### **Infrastructure Level**
- [ ] All required ports open between nodes (2377, 7946, 4789)
- [ ] Kernel modules loaded (bridge, ip_tables, nf_nat, overlay, br_netfilter)
- [ ] Firewall rules permit cluster communication
- [ ] No network interface checksum offloading issues

### **Docker Swarm Level**
- [ ] All nodes in "Ready" state
- [ ] Proper node IP addresses configured
- [ ] Ingress network contains service containers
- [ ] Service ports properly published with "ingress" mode

### **Service Level**
- [ ] Services respond to internal health checks
- [ ] DNS resolution works for service names
- [ ] Traefik labels correctly formatted
- [ ] Services connected to proper networks

### **Application Level**
- [ ] Applications bind to 0.0.0.0 (not localhost)
- [ ] Health check endpoints respond correctly
- [ ] No port conflicts between services
- [ ] Proper service dependencies configured

---

## 🔄 **Systematic Troubleshooting Process**

### **Step 1: Quick Validation**
```bash
# Test basic connectivity
curl -s http://localhost:80/ --connect-timeout 2  # Should work (Traefik)
curl -s http://localhost:<service-port>/ --connect-timeout 2  # Test target service
```

### **Step 2: Infrastructure Assessment**
```bash
# Run infrastructure diagnostics
nc -zv <node-ip> 2377 7946 4789
lsmod | grep -E "(bridge|ip_tables|nf_nat|overlay|br_netfilter)"
docker node ls
```

### **Step 3: Service-Specific Testing**
```bash
# Test direct service connectivity
curl -s http://<node-ip>:<service-port>/health
docker service ps <service-name>
docker service inspect <service-name> --format '{{json .Endpoint.Ports}}'
```

### **Step 4: Network Deep Dive**
```bash
# Analyze network configuration
docker network inspect ingress
docker network inspect <service-network>
ss -tulpn | grep <service-port>
```

### **Step 5: Resolution Implementation**
```bash
# Apply fixes based on findings
sudo ufw allow from 192.168.1.0/24 to any  # Fix firewall
sudo modprobe overlay bridge  # Fix kernel modules
docker service update --force <service-name>  # Reset service
```

---

## 📚 **Reference Documentation**

### **Official Docker Documentation**
- [Docker Swarm Networking](https://docs.docker.com/engine/swarm/networking/)
- [Routing Mesh](https://docs.docker.com/engine/swarm/ingress/)
- [Overlay Networks](https://docs.docker.com/engine/network/drivers/overlay/)

### **Official Traefik Documentation**
- [Traefik Docker Swarm Provider](https://doc.traefik.io/traefik/providers/swarm/)
- [Traefik Swarm Routing](https://doc.traefik.io/traefik/routing/providers/swarm/)

### **Community Resources**
- [Docker Swarm Rocks - Traefik Guide](https://dockerswarm.rocks/traefik/)
- [Docker Forums - Routing Mesh Issues](https://forums.docker.com/c/swarm/17)

---

## 🎯 **Key Insights**

### **Critical Understanding**
1. **Routing Mesh vs Service Discovery**: Traefik uses overlay networks for service discovery, not the routing mesh
2. **Port Requirements**: Specific ports (2377, 7946, 4789) must be open between ALL nodes
3. **Kernel Dependencies**: Overlay networks require specific kernel modules
4. **Firewall Impact**: Most routing mesh issues are firewall-related

### **Best Practices**
1. **Always test infrastructure first** before troubleshooting applications
2. **Use permissive firewall rules** for internal cluster communication
3. **Verify kernel modules** in containerized environments
4. **Test routing mesh systematically** across all nodes

### **Common Pitfalls**
1. **Assuming localhost works**: Docker Swarm routing mesh may not bind to localhost
2. **Ignoring kernel modules**: Missing modules cause silent failures
3. **Firewall confusion**: UFW rules may not cover all Docker traffic
4. **Service placement assumptions**: Placement constraints can break routing

---

## 🚀 **Quick Reference Commands**

### **Infrastructure Testing**
```bash
# Test all required ports
for port in 2377 7946 4789; do nc -zv <node-ip> $port; done

# Check kernel modules
lsmod | grep -E "(bridge|ip_tables|nf_nat|overlay|br_netfilter)"

# Test routing mesh
curl -s http://localhost:<port>/ --connect-timeout 5
```

### **Service Diagnostics**
```bash
# Service health check
docker service ps <service-name>
docker service inspect <service-name> --format '{{json .Endpoint.Ports}}'
curl -s http://<node-ip>:<port>/health
```

### **Network Analysis**
```bash
# Network inspection
docker network inspect ingress
docker network inspect <service-network>
ss -tulpn | grep <port>
```

---

**This guide should be referenced whenever Docker Swarm networking issues arise, providing a systematic approach to diagnosis and resolution.**