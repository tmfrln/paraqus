!   Paraqus - A VTK exporter for FEM results.
!
!   Copyright (C) 2022, Furlan, Stollberg and Menzel
!
!    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
!
!    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General !Public License for more details.
!
!    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.
!
!
!   Example user material subroutine for the extrusion example
!   The user material implements finite strain elasto-plasticity in terms of a von Mises plasticity, formulated in Mandel stresses, and includes isotropic hardening. An exponential map is implemented for the time integration.
!
       SUBROUTINE UMAT(STRESS,STATEV,DDSDDE,SSE,SPD,SCD,RPL,DDSDDT,
     &                  DRPLDE,DRPLDT,STRAN,DSTRAN,TIME,DTIME,TEMP,
     &                  DTEMP,PREDEF,DPRED,CMNAME,NDI,NSHR,NTENS,NSTATV,
     &                  PROPS,NPROPS,COORDS,DROT,PNEWDT,CELENT,DFGRD0,
     &                  DFGRD1,NOEL,NPT,LAYER,KSPT,KSTEP,KINC)
     
            IMPLICIT REAL*8(a-h,o-z)
            !INCLUDE 'SMAAspUserArrays.hdr'
        
            CHARACTER*80 CMNAME
            DIMENSION STRESS(NTENS),STATEV(NSTATV),DDSDDE(NTENS,NTENS),
     &                DDSDDT(NTENS),DRPLDE(NTENS),STRAN(NTENS),
     &                DSTRAN(NTENS),TIME(2),PREDEF(1),DPRED(1),
     &                PROPS(NPROPS),COORDS(3),DROT(3,3),DFGRD0(3,3),
     &                DFGRD1(3,3)
            
            DOUBLE PRECISION, DIMENSION(3,3,3,3) :: dP_dF,dSigma_dG
            DOUBLE PRECISION, DIMENSION(3,3,3,3) :: DDSDDE_tens
            DOUBLE PRECISION, DIMENSION(3,3)     :: P,sigma
            DOUBLE PRECISION, DIMENSION(6)       :: matParams
            DOUBLE PRECISION                     :: detJ
            INTEGER, DIMENSION(3)                :: NDIMS
            
            matParams = PROPS
            CALL CALCDET33(DFGRD1, detJ)
            NDIMS(1) = NDI
            NDIMS(2) = NSHR
            NDIMS(3) = NTENS
            
            !-----------------------------------------------------------
            ! Constitutive model
            CALL constitutiveModel(DFGRD1,STATEV,matParams,P,KINC,dP_dF,PNEWDT)
                        
            !-----------------------------------------------------------
            ! Push-Forward
            sigma = MATMUL(DFGRD1,P)/detJ
            CALL PUSHFORWARDDPDF(dP_dF,DFGRD1,sigma,dSigma_dG)
            
            !-----------------------------------------------------------
            ! Jaumann Correction
            CALL JaumannCorrection(sigma,dSigma_dG,DDSDDE_tens)
            
            !-----------------------------------------------------------
            ! Voigt transformation
            CALL TENSOR33TOVOIGT(sigma,NDIMS,STRESS)
            CALL T3333TOVOIGT(DDSDDE_tens,NDIMS,DDSDDE)
            
        END SUBROUTINE
    

!-----------------------------------------------------------------------
! Constitutive Model
!-----------------------------------------------------------------------
        SUBROUTINE constitutiveModel(F,STATEV,matParams,P,KINC,C4algo,PNEWDT)
                   
            DOUBLE PRECISION :: E,nu,q0,q_sat,alpha_u,h,mu,lam
            DOUBLE PRECISION :: alpha,alpha_n,detJe,detCe,devM_norm
            DOUBLE PRECISION :: tol,phi,dlambda,res,PNEWDT
            DOUBLE PRECISION :: Dphi_Ddlambda,devFp_norm
            
            DOUBLE PRECISION, DIMENSION(6)       :: matParams
            DOUBLE PRECISION, DIMENSION(3,3)     :: Dphi_DFp,DR_Fp_Ddlambda
            DOUBLE PRECISION, DIMENSION(3,3)     :: F,Fp,Fp_n,ident,zeros
            DOUBLE PRECISION, DIMENSION(3,3)     :: Fp_inv,Fe,Fe_trans,Ce
            DOUBLE PRECISION, DIMENSION(3,3)     :: M,devM,N,expLP,Fe_inv
            DOUBLE PRECISION, DIMENSION(3,3)     :: P,R_Fp,devFp,Dphi_DF
            DOUBLE PRECISION, DIMENSION(3,3,3,3) :: dexpdLP,DR_Fp_DFp
            DOUBLE PRECISION, DIMENSION(3,3,3,3) :: DR_Fp_DF,DP_DFp
            DOUBLE PRECISION, DIMENSION(3,3,3,3) :: C4algo_p,C4algo,DP_DF
            DOUBLE PRECISION, DIMENSION(10)      :: R,x,xn
            DOUBLE PRECISION, DIMENSION(11)      :: STATEV
            DOUBLE PRECISION, DIMENSION(10,10)   :: DR,DR_inv
            DOUBLE PRECISION, DIMENSION(10,3,3)  :: DR_DF
            DOUBLE PRECISION, DIMENSION(3,3,10)  :: dP_dx
            INTEGER :: maxIter,iter,KINC
            INTEGER :: ii,jj,kk,ll,mm,nn
            DOUBLE PRECISION, DIMENSION(10,10)   :: DR_test,DR_test_inv

            !-----------------------------------------------------------
            ! Newton tolerance
            tol = 10.0d0**(-8.0d0)
            ! Maximum number of Newton iterations
            maxIter = 15
            
            !-----------------------------------------------------------
            ! youngs modulus
            E        = matParams(1)
            ! poissions ratio
            nu       = matParams(2)
            ! plastic threshold
            q0       = matParams(3)
            ! plastic saturation
            q_sat    = matParams(4)
            ! hardening parameter
            alpha_u  = matParams(5)
            ! hardening modulus
            h        = matParams(6)
            ! convert 'E' and 'nu' to Lame parameters (mue and lambda)
            mu       = E/(2.0d0*(1.0d0+nu))
            lam      = E*nu/((1.0d0+nu)*(1.0d0-2.0d0*nu))
            
            !-----------------------------------------------------------
            ! identity matrix
            CALL IDENTITY(ident)
            
            ! initialize plastic deformation
            ! as an alternative, the internal variables can get initial
            ! conditions in abaqus
            Fp_n = 0.0d0
            IF (KINC == 0) THEN
                Fp_n        = ident
                alpha_n     = 0.0d0
            ELSE IF (KINC == 1) THEN
                Fp_n        = ident
                alpha_n     = 0.0d0
            ELSE
                Fp_n = RESHAPE(STATEV(2:10),(/3,3/))
                alpha_n   = STATEV(1)
            END IF

            !-----------------------------------------------------------
            ! Predictor step
            ! Predictor
            Fp          = Fp_n
            alpha       = alpha_n
            zeros       = 0.0d0
            
            CALL CALCINV33(Fp, Fp_inv)
            Fe          = MATMUL(F, Fp_inv)
            CALL CALCDET33(Fe, detJe)
            Fe_trans    = TRANSPOSE(Fe)
            Ce          = MATMUL(Fe_trans, Fe)

            ! Mandelspannungen
            M = (0.5d0*lam*(detJe**(2.0d0)-1.0d0)-mu)*ident + mu*Ce
            CALL Deviator(M,devM)
            CALL FROBNORM33(devM, devM_norm)
            
            ! Fließfunktion
            phi = devM_norm-q0-q_sat*(1.0d0-exp(alpha/alpha_u))+h*alpha

            !-----------------------------------------------------------
            ! Corrector step
            ! Corrector
            IF (phi > 0.0d0) THEN

                ! trial residual vector
                R       = 0.0d0
                R(1)    = phi
                ! trial residual
                res     = phi
                ! initialize tangent
                DR      = 0.0d0
                ! Lp direction
                N       = devM/devM_norm
                ! initial plastic multiplier
                dLambda = 0.0d0
                ! exponential map
                CALL ExponentialMap(zeros, expLP, dexpdLP)
                
                ! iteration
                iter = 0
                DO WHILE (res>tol)
                    
                    ! tangents
                    Dphi_Ddlambda = -q_sat/alpha_u*exp(alpha/alpha_u)-h
                    Dphi_DFp = -2.0d0*mu*MATMUL(MATMUL(Ce,N),TRANSPOSE(Fp_inv))
                    CALL calc_DR_Fp_Ddlambda(Fp_n,N,dexpDLp,DR_Fp_Ddlambda)
                    CALL calc_DR_Fp_DFp(Fp,Fp_n,Ce,dlambda,DexpDLp,devM,mu,lam,DR_Fp_DFp)
                    
                    ! tangent assembly
                    DR(1,1)         = Dphi_Ddlambda
                    DR(2:10,1)      = RESHAPE(DR_Fp_Ddlambda,(/9/))
                    DR(1,2:10)      = RESHAPE(Dphi_DFp,(/9/))
                    DR(2:10,2:10)   = RESHAPE(DR_Fp_DFp,(/9,9/))
                    
                    ! Newton update
                    xn(1)           = dLambda
                    xn(2:10)        = RESHAPE(Fp,(/9/))
                    CALL CALCINV1010(DR, DR_inv)
                    x               = xn - MATMUL(DR_inv,R)
                    dLambda         = x(1)
                    Fp              = RESHAPE(x(2:10),(/3,3/))
                    CALL CALCINV33(Fp, Fp_inv)
                    
                    ! calculate new residual
                    Fe              = MATMUL(F,Fp_inv)
                    CALL CALCDET33(Fe, detJe)
                    Fe_trans        = TRANSPOSE(Fe)
                    Ce              = MATMUL(Fe_trans, Fe)
                    
                    M = (0.5d0*lam*(detJe**(2.0d0)-1.0d0)-mu)*ident+mu*Ce
                    CALL Deviator(M,devM)
                    CALL FROBNORM33(devM, devM_norm)
                    N               = devM/devM_norm
                    alpha           = alpha_n - dLambda
                    phi = devM_norm-q0-q_sat*(1.0d0-exp(alpha/alpha_u))+h*alpha
                    CALL ExponentialMap(dLambda*N, expLP, dexpdLP)
                    R_Fp = Fp - MATMUL(expLP,Fp_n)
                    R(1) = phi
                    R(2:10) = RESHAPE(R_Fp,(/9/))
                    CALL EUCLIDNORM(R, res)
                    
                    iter = iter + 1
                    IF (iter > maxIter) THEN
                        write(*,*) 'local Newton did not converge in ', KINC
                        write(*,*) ' Residuum: ', res
                        PNEWDT = 0.50d0
                        EXIT
                    END IF
                    
                END DO
            
                ! tangents
                Dphi_Ddlambda = -q_sat/alpha_u*exp(alpha/alpha_u)-h
                Dphi_DFp = -2.0d0*mu*MATMUL(MATMUL(Ce,N),TRANSPOSE(Fp_inv))
                CALL calc_DR_Fp_Ddlambda(Fp_n,N,dexpDLp,DR_Fp_Ddlambda)
                CALL calc_DR_Fp_DFp(Fp,Fp_n,Ce,dlambda,DexpDLp,devM,mu,lam,DR_Fp_DFp)
                
                ! tangent assembly
                DR(1,1)         = Dphi_Ddlambda
                DR(2:10,1)      = RESHAPE(DR_Fp_Ddlambda,(/9/))
                DR(1,2:10)      = RESHAPE(Dphi_DFp,(/9/))
                DR(2:10,2:10)   = RESHAPE(DR_Fp_DFp,(/9,9/))
                
                ! Conditional partof the algorithmic tangent
                CALL CALCINV1010(DR, DR_inv)
                DR_DF = 0.0d0
                
                CALL calcDR_Fp_DF__dP_dFp(dLambda,DexpDLp,devM,Fp_n,F,Fe,
     &                                    Fp,lam,mu,DR_Fp_DF,DP_DFp)
     
                Dphi_DF = 2.0d0*mu*MATMUL(MATMUL(Fe,N),TRANSPOSE(Fp_inv))
                
                DR_DF(1,1:3,1:3) = Dphi_DF
                DR_DF(2:10,1:3,1:3) = RESHAPE(DR_Fp_DF,(/9,3,3/))
                
                dP_dx = 0.0d0
                dP_dx(:,:,1) = 0.0d0
                dP_dx(:,:,2:10) = RESHAPE(DP_DFp,(/3,3,9/))
                
                C4algo_p = 0.0d0
                DO ll=1,3
                    DO kk=1,3
                        DO jj=1,3
                            DO ii=1,3
                                DO nn=1,10
                                    DO mm=1,10
                                        C4algo_p(ii,jj,kk,ll)=
     & C4algo_p(ii,jj,kk,ll)-dP_dx(ii,jj,nn)*DR_inv(nn,mm)*DR_DF(mm,kk,ll)
                                    END DO
                                END DO
                            END DO
                        END DO
                    END DO
                END DO
                
                CALL calcDP_DF(F,Fp,detJe,mu,lam,DP_DF)
                C4algo = DP_DF + C4algo_p
            
            ELSE
                CALL calcDP_DF(F,Fp,detJe,mu,lam,DP_DF)
                C4algo = DP_DF
            END IF
            
            CALL CALCINV33(Fe, Fe_inv)
            P = MATMUL(MATMUL(TRANSPOSE(Fe_inv),M),TRANSPOSE(Fp_inv))
                
            CALL Deviator(Fp,devFp)
            CALL FROBNORM33(devFp, devFp_norm)
            STATEV(1)       = alpha
            STATEV(2:10)    = RESHAPE(Fp,(/9/))
            STATEV(11)      = devFp_norm
            
        END SUBROUTINE

!-----------------------------------------------------------------------
! Tangents
!-----------------------------------------------------------------------

        SUBROUTINE calcDP_DF(F,Fp,detJe,mu,lam,DP_DF)
        
            DOUBLE PRECISION, DIMENSION(3,3,3,3) :: DP_DF
            DOUBLE PRECISION, DIMENSION(3,3)     :: F,Fp,F_inv,Fp_inv
            DOUBLE PRECISION, DIMENSION(3,3)     :: ident
            DOUBLE PRECISION                     :: detJe,mu,lam
            INTEGER :: ii,jj,kk,ll,pp
            
            CALL CALCINV33(F, F_inv)
            CALL CALCINV33(Fp, Fp_inv)
            CALL IDENTITY(ident)
            
            DP_DF = 0.0d0
            DO ii=1,3
                DO jj=1,3
                    DO kk=1,3
                        DO ll=1,3
                            DP_DF(ii,jj,kk,ll)=DP_DF(ii,jj,kk,ll)
     & +lam*detJe**(2.0d0)*F_inv(ll,kk)*F_inv(jj,ii)
     & -(lam/2.0d0*(detJe**(2.0d0)-1.0d0)-mu)*F_inv(ll,ii)*F_inv(jj,kk)
                            DO pp=1,3
                                DP_DF(ii,jj,kk,ll)=DP_DF(ii,jj,kk,ll) 
     & +mu*ident(ii,kk)*Fp_inv(ll,pp)*Fp_inv(jj,pp)
                            END DO
                        END DO
                    END DO
                END DO
            END DO
            
        END SUBROUTINE
        
        SUBROUTINE calcDR_Fp_DF__dP_dFp(dLambda,DexpDLp,devM,Fp_n,F,Fe,
     &                                  Fp,lam,mu,DR_Fp_DF,DP_DFp)
            
            DOUBLE PRECISION, DIMENSION(3,3,3,3) :: DexpDLp,DP_DFp,DN_DM
            DOUBLE PRECISION, DIMENSION(3,3,3,3) :: DM_DF,DN_DF,DR_Fp_DF
            DOUBLE PRECISION, DIMENSION(3,3)     :: devM,Fp_n,F,Fe,Fp,Cp
            DOUBLE PRECISION, DIMENSION(3,3)     :: ident,Fp_inv,F_inv
            DOUBLE PRECISION, DIMENSION(6)       :: matParams
            DOUBLE PRECISION                     :: devM_norm,detJe
            DOUBLE PRECISION                     :: lam,mu,dLambda
            INTEGER :: ii,jj,kk,ll,mm,nn,oo,pp,qq,rr,ss
            
            CALL FROBNORM33(devM, devM_norm)
            CALL IDENTITY(ident)
            CALL CALCDET33(Fe, detJe)
            CALL CALCINV33(Fp, Fp_inv)
            CALL CALCINV33(F, F_inv)
            
            DP_DFp = 0.0d0
            
            DO ii=1,3
                DO jj=1,3
                    DO kk=1,3
                        DO ll=1,3
                            DP_DFp(ii,jj,kk,ll)=
     & -lam*detJe**(2.0d0)*F_inv(jj,ii)*Fp_inv(ll,kk)
                            DO pp=1,3
                                DP_DFp(ii,jj,kk,ll)=DP_DFp(ii,jj,kk,ll)
     & -mu*Fe(ii,kk)*Fp_inv(ll,pp)*Fp_inv(jj,pp)
     & -mu*Fe(ii,pp)*Fp_inv(ll,pp)*Fp_inv(jj,kk)
                            END DO
                        END DO
                    END DO
                END DO
            END DO
            
            DN_DM = 0.0d0
            DO pp=1,3
                DO qq=1,3
                    DO rr=1,3
                        DO ss=1,3
                            DN_DM(pp,qq,rr,ss)=
     & ((ident(pp,rr)*ident(qq,ss) + ident(pp,ss)*ident(qq,rr))/2.0d0 
     & -ident(pp,qq)*ident(rr,ss)/3.0d0)/devM_norm
     & -devM(pp,qq)*devM(rr,ss)/(devM_norm**(3.0d0))
                        END DO
                    END DO
                END DO
            END DO
            
            DM_DF = 0.0d0
            DO rr=1,3
                DO ss=1,3
                    DO kk=1,3
                        DO ll=1,3
                            DM_DF(rr,ss,kk,ll)=
     & +lam*detJe*(2.0d0)*ident(rr,ss)*F_inv(ll,kk)
     & +mu*(Fp_inv(ll,rr)*Fe(kk,ss)+Fp_inv(ll,ss)*Fe(kk,rr))
                        END DO
                    END DO
                END DO
            END DO
            
            CALL T4DDT4(DN_DM,DM_DF,DN_DF)
            
            DR_Fp_DF = 0.0d0
            DO ii=1,3
                DO jj=1,3
                    DO kk=1,3
                        DO ll=1,3
                            DO mm=1,3
                                DO nn=1,3
                                DR_Fp_DF(ii,jj,kk,ll)=DR_Fp_DF(ii,jj,kk,ll)
     & -dLambda*dot_product(DexpDLp(ii,:,mm,nn),Fp_n(:,jj))*DN_DF(mm,nn,kk,ll)
                                END DO
                            END DO
                        END DO
                    END DO
                END DO
            END DO
            
        END SUBROUTINE
                
        ! Tangent 1 of local const model
        SUBROUTINE calc_DR_Fp_DFp(Fp,Fp_n,Ce,dlambda,DexpDLp,devM,mu,lam,DR_Fp_DFp)
            
            DOUBLE PRECISION, DIMENSION(3,3,3,3) :: DN_DM,DM_DFp,DN_DFp
            DOUBLE PRECISION, DIMENSION(3,3,3,3) :: DR_Fp_DFp,DexpDLp
            DOUBLE PRECISION, DIMENSION(3,3)     :: Fp,Fp_n,Ce,devM
            DOUBLE PRECISION, DIMENSION(3,3)     :: ident,Fp_inv
            DOUBLE PRECISION                     :: devM_norm,mu,lam,detCe
            DOUBLE PRECISION                     :: dlambda
            INTEGER                              :: ii,jj,kk,ll,mm,nn
            
            CALL IDENTITY(ident)
            CALL FROBNORM33(devM, devM_norm)
            CALL CALCINV33(Fp, Fp_inv)
            CALL CALCDET33(Ce, detCe)
            
            DN_DM = 0.0d0
            DO ii=1,3
                DO jj=1,3
                    DO mm=1,3 
                        DO nn=1,3
                            DN_DM(ii,jj,mm,nn) = 
     & (ident(ii,mm)*ident(jj,nn)-ident(mm,nn)*ident(ii,jj)/3.0d0)/devM_norm
     & - devM(ii,jj)*devM(mm,nn)/(devM_norm**(3.0d0))
                        END DO
                    END DO
                END DO
            END DO
            
            
            
            DM_DFp = 0.0d0
            DO ii=1,3
                DO jj=1,3
                    DO kk=1,3
                        DO ll=1,3
                            DM_DFp(ii,jj,kk,ll) = 
     & -lam*detCe*ident(ii,jj)*Fp_inv(ll,kk)
     & -mu*(Fp_inv(ll,ii)*Ce(jj,kk)+Fp_inv(ll,jj)*Ce(ii,kk))
                        END DO
                    END DO
                END DO
            END DO
            
            CALL T4DDT4(DN_DM,DM_DFp,DN_DFp)
            
            DR_Fp_DFp = 0.0d0
            DO ii=1,3
                DO jj=1,3
                    DO kk=1,3
                        DO ll=1,3
                            DR_Fp_DFp(ii,jj,kk,ll)=ident(ii,kk)*ident(jj,ll)
                            DO mm=1,3
                                DO nn=1,3
                                    DR_Fp_DFp(ii,jj,kk,ll)=DR_Fp_DFp(ii,jj,kk,ll)
     & -dlambda*dot_product(DexpDLp(ii,:,mm,nn), Fp_n(:,jj))*DN_DFp(mm,nn,kk,ll)
                                END DO
                            END DO
                        END DO
                    END DO
                END DO
            END DO
                    
        END SUBROUTINE

        ! Tangent 2 of local const model
        SUBROUTINE calc_DR_Fp_Ddlambda(Fp_n,N,DexpDLp,DR_Fp_Ddlambda)
            
            DOUBLE PRECISION, DIMENSION(3,3)     :: DR_Fp_Ddlambda
            DOUBLE PRECISION, DIMENSION(3,3)     :: DexpDLp_Ddlambda
            DOUBLE PRECISION, DIMENSION(3,3)     :: N,Fp_n
            DOUBLE PRECISION, DIMENSION(3,3,3,3) :: DexpDLp
            INTEGER                              :: jj,ii
            
            DR_Fp_Ddlambda = 0.0d0
            DexpDLp_Ddlambda = 0.0d0
            
            DO jj=1,3
                DO ii=1,3
                    DexpDLp_Ddlambda = DexpDLp_Ddlambda 
     & + DexpDLp(:,:,ii,jj)*N(ii,jj)
                END DO
            END DO
            
            DR_Fp_Ddlambda = -MATMUL(DexpDLp_Ddlambda,Fp_n)
                    
        END SUBROUTINE    
    
!-----------------------------------------------------------------------
! Helper Routines
!-----------------------------------------------------------------------

        ! Compute Voigt Notation of 3x3 tensor
        SUBROUTINE TENSOR33TOVOIGT(Tensor3x3,N,List1xN)
              
            INTEGER, INTENT(IN) :: N(3)
            DOUBLE PRECISION, DIMENSION(3,3), INTENT(IN)  :: Tensor3x3
            DOUBLE PRECISION, DIMENSION(N(3)),   INTENT(OUT) :: List1xN
            INTEGER, DIMENSION(3) :: i1, i2
            INTEGER :: i
            
            i1(1:3) = (/ 1, 1, 2 /)
            i2(1:3) = (/ 2, 3, 3 /)
            
            DO i=1,N(1)
                List1xN(i) = Tensor3x3(i,i)
            END DO
            
            DO i=1,N(2)
                List1xN(N(1)+i) = Tensor3x3(i1(i),i2(i))
            END DO
        
        END SUBROUTINE
        
        ! Perform Voigt transformation
        SUBROUTINE T3333TOVOIGT(TensorT4,N,MatrixNxN)
        
            ! transforms a 4th order abaqus tangent tensor to a 6x6 Matrix format
            INTEGER, INTENT(IN) :: N(3)
            DOUBLE PRECISION, DIMENSION(3,3,3,3), INTENT(IN)  :: TensorT4
            DOUBLE PRECISION, DIMENSION(N(3),N(3)),     INTENT(OUT) :: MatrixNxN
            
            INTEGER, DIMENSION(3) :: i1, i2
            INTEGER :: i, j
         
            i1(1:3) = (/ 1, 1, 2 /)
            i2(1:3) = (/ 2, 3, 3 /)
         
            DO i=1,N(1)
                DO j=1,N(1)
                    MatrixNxN(i,j) = TensorT4(i,i,j,j)
                END DO
                DO j=1,N(2)
                    MatrixNxN(i,N(1)+j) = TensorT4(i,i,i1(j),i2(j))
                END DO
            END DO
            DO i=1,N(2)
                DO j=1,N(1)
                    MatrixNxN(N(1)+i,j) = TensorT4(i1(i),i2(i),j,j)
                END DO
                DO j=1,N(2)
                    MatrixNxN(N(1)+i,N(1)+j) = TensorT4(i1(i),i2(i),i1(j),i2(j))
                END DO
            END DO
        
        END SUBROUTINE
        
        ! Perform the Push-Forward of the tangent DPDF to sigma related
        SUBROUTINE PUSHFORWARDDPDF(DPDF,F,sigma,DSIGDG)
            
              !Input
              DOUBLE PRECISION, DIMENSION(3,3,3,3)    :: DPDF
              DOUBLE PRECISION, DIMENSION(3,3)        :: F, sigma
            
              ! Output
              DOUBLE PRECISION, DIMENSION(3,3,3,3)    :: DSIGDG
            
              ! Internal variable
              DOUBLE PRECISION, DIMENSION(3,3)        :: ident, Ftrans
              DOUBLE PRECISION                        :: detJ
              INTEGER                                 :: i,j,k,l,m,n,o
            
            
              CALL IDENTITY(ident)
             
              CALL CALCDET33(F, detJ)
            
              Ftrans = TRANSPOSE(F)
            
              DSIGDG = 0.0d0
            
              DO i = 1,3
                DO j = 1,3
                    DO k = 1,3
                        DO l = 1,3
                            DO m = 1,3
                                DO n = 1,3
                                    DO o = 1,3
                                        DSIGDG(i,j,m,o) = DSIGDG(i,j,m,o) 
     &                 + ident(i,k)*F(j,l)*DPDF(k,l,m,n)*Ftrans(n,o)/detJ
                                    END DO
                                END DO
                            END DO
                        END DO
                    END DO
                END DO
              END DO 
            
              DO i = 1,3
                DO j = 1,3
                    DO m = 1,3
                        DO o = 1,3
                            DSIGDG(i,j,m,o) = DSIGDG(i,j,m,o) 
     &                                - ident(i,m)*sigma(j,o)
                        END DO
                    END DO
                END DO
              END DO
        
        END SUBROUTINE
        
        ! Perform the Jaumann Correction
        SUBROUTINE JaumannCorrection(sigma,DsigmaDg,DDSDDEtens)
            
              DOUBLE PRECISION, DIMENSION(3,3,3,3) :: DsigmaDg, DDSDDEtens
              DOUBLE PRECISION, DIMENSION(3,3) :: sigma, eye
              INTEGER :: i, j, k, l
            
              ! add Jaumann rate correction to DsigmaDg for the final
              ! Abaqus tangent DDSDDE (as 4th order tensor):
              ! required here: Cauchy stress (3.42)
            
              eye = 0.0d0
              forall(i = 1:3) eye(i,i) = 1.0d0
            
              DO i = 1,3
                DO j = 1,3
                    DO k = 1,3
                        DO l = 1,3
                            DDSDDEtens(i,j,k,l) = DsigmaDg(i,j,k,l)
     &                        + eye(i,k)*sigma(j,l)
     &                        + sigma(i,k)*eye(j,l)
                        END DO
                    END DO
                END DO
              END DO
            
        END SUBROUTINE
        
        ! Calculate the exponential map
        SUBROUTINE ExponentialMap(A, expA, dexpA)
            
            
            ! Calculate the exponential function of the matrix and its
            ! derivative using a taylor expansion
            
            INTEGER                              :: maxIter,totalIter
            INTEGER                              :: nn,mm,ll,kk,jj,ii
            DOUBLE PRECISION                     :: tol,nfac,summand_norm
            DOUBLE PRECISION, DIMENSION(3,3)     :: A,expA,ident,summand
            DOUBLE PRECISION, DIMENSION(3,3,171) :: Atimes
            DOUBLE PRECISION, DIMENSION(3,3,3,3) :: dexpA,summand4
            
            maxIter = 170
            Atimes = 0.0d0
            totalIter = maxIter
            tol = 10.0d0**(-15.0d0)
            nfac = 1.0d0
            CALL IDENTITY(ident)
            
            ! exponential of matrix
            Atimes(:,:,1) = ident
            Atimes(:,:,2) = A
            
            expA = 0.0d0
            DO nn = 1,maxIter+1
                expA = expA + Atimes(:,:,nn)
            END DO
            
            DO nn = 2,maxIter
                nfac = nfac*nn
                Atimes(:,:,nn+1) = Atimes(:,:,nn)*A
                summand = 1.0d0/nfac*Atimes(:,:,nn+1)
                
                ! Check convergence
                CALL FROBNORM33(summand, summand_norm)
                IF (summand_norm < tol) THEN
                    totalIter = nn-1
                    EXIT
                END IF
                
                expA = expA + summand
            
            END DO
            
            ! Derivative
            dexpA = 0.0d0
            nfac = 1.0d0
            DO nn = 1,totalIter
                nfac = nfac*nn
                summand4 = 0.0d0
                DO mm = 1,nn
                    DO ll = 1,3
                        DO kk = 1,3
                            DO jj = 1,3
                                DO ii = 1,3
                                    summand4(ii,jj,kk,ll) = summand4(ii,jj,kk,ll)
     &                              + Atimes(ii,kk,mm)*Atimes(ll,jj,nn-mm+1)
                                END DO
                            END DO
                        END DO
                    END DO
                END DO
                dexpA = dexpA + 1.0d0/nfac*summand4
            END DO
            
        END SUBROUTINE

        ! Compute the deviatoric part of a tensor
        SUBROUTINE Deviator(A,Adev)
              
              DOUBLE PRECISION :: trace
              DOUBLE PRECISION, DIMENSION(3,3) :: A,Adev,ident
              INTEGER :: i
	
              CALL IDENTITY(ident)
              trace = 0.0d0
              DO i = 1,3
                trace = trace + A(i,i)
              END DO
              
              Adev = A - trace*ident/3.0d0
	
        END SUBROUTINE

        ! Compute the identity matrix
        SUBROUTINE IDENTITY(Ident)
              
              DOUBLE PRECISION, DIMENSION(3,3) :: Ident
              INTEGER :: i
	
              Ident = 0.0d0
              DO i = 1,3
                Ident(i,i) = 1.0d0
              END DO
	
        END SUBROUTINE

       ! Compute inverse of a 10x10 matrix
        SUBROUTINE CALCINV1010(A, Ainv)
            
              DOUBLE PRECISION, dimension(10,10) :: A, Ainv
              DOUBLE PRECISION :: lwork(10)
              INTEGER :: info
              INTEGER :: n=10
              INTEGER :: ipiv(10)
              EXTERNAL DGETRI, DGETRF
		
              Ainv = A
		
              CALL DGETRF(n,n,Ainv,n,ipiv,info)
		
              If (info==0) Then
                CALL DGETRI(n,Ainv,n,ipiv,lwork,n,info)
              Else
                PRINT *, '10x10 matrix is singular'
              End If
        
        END SUBROUTINE
       
       ! Compute inverese of a 3x3 matrix
        SUBROUTINE CALCINV33(A, Ainv)
            
              DOUBLE PRECISION, dimension(3,3) :: A, Ainv
              DOUBLE PRECISION :: lwork(3)
              INTEGER :: info
              INTEGER :: n=3
              INTEGER :: ipiv(3)
              EXTERNAL DGETRI, DGETRF
		
              Ainv = A
		
              CALL DGETRF(n,n,Ainv,n,ipiv,info)
		
              If (info==0) Then
                CALL DGETRI(n,Ainv,n,ipiv,lwork,n,info)
              Else
                write(*,*) A(1,1),A(1,2),A(1,3)
                write(*,*) A(2,1),A(2,2),A(2,3)
                write(*,*) A(3,1),A(3,2),A(3,3) 
                PRINT *, '3x3 matrix is singular'
              End If
        
        END SUBROUTINE
        
        ! Compute determinant of a 3x3 matrix
        SUBROUTINE CALCDET33(A, detA)
            
              DOUBLE PRECISION, DIMENSION(3,3) :: A
              DOUBLE PRECISION :: detA
            
              detA = A(1,1)*(A(2,2)*A(3,3) - A(3,2)*A(2,3))
     &          + A(1,2)*(A(3,1)*A(2,3) - A(2,1)*a(3,3))
     &          + A(1,3)*(A(2,1)*A(3,2) - A(3,1)*a(2,2))
        
        END SUBROUTINE

        ! Calculate a euclidean norm for a 10x10 vector
        SUBROUTINE EUCLIDNORM(a, anorm)
            
            DOUBLE PRECISION, DIMENSION(10) :: a
            DOUBLE PRECISION                :: anorm
            INTEGER                         :: ii
            
            anorm = 0.0d0
            DO ii=1,10
                anorm = anorm + a(ii)**(2.0d0)
            END DO
            
            anorm = SQRT(anorm)
        END SUBROUTINE
        
        ! Calculate the frobenius norm of a 3x3 matrix
        SUBROUTINE FROBNORM33(A, Anorm)
        
              DOUBLE PRECISION, DIMENSION(3,3) :: A
              DOUBLE PRECISION                 :: Anorm
            
              INTEGER                          :: i,j
            
              Anorm = 0.0d0
              DO i = 1,3
                DO j = 1,3
                    Anorm = Anorm + A(i,j)**(2.0d0)
                END DO
              END DO
            
              Anorm = SQRT(Anorm)
        
        END SUBROUTINE
        
        ! Calculate the double contraction of two fourth order tensors
        SUBROUTINE T4DDT4(A,B,C)

            DOUBLE PRECISION, DIMENSION(3,3,3,3) :: A,B,C
            INTEGER :: ii,jj,kk,ll,oo,pp
            
            C = 0.0d0
            DO ii=1,3
                DO jj=1,3
                    DO kk=1,3
                        DO ll=1,3
                            DO oo=1,3
                                DO pp=1,3
                                    C(ii,jj,oo,pp)=C(ii,jj,oo,pp) 
     & +A(ii,jj,kk,ll)*B(kk,ll,oo,pp)
                                END DO
                            END DO
                        END DO
                    END DO
                END DO
            END DO
            
        END SUBROUTINE
        
        ! Calculate the single contraction of two two order tensors
        SUBROUTINE T2DT2(A,B,C)
        
            DOUBLE PRECISION, DIMENSION(3,3) :: A,B,C
            INTEGER                          :: ii,jj,kk
            
            C = 0.0d0
            
            DO ii=1,3
                DO jj=1,3
                    DO kk=1,3
                        C(ii,jj) = C(ii,jj) + A(ii,kk)*B(kk,jj)
                    END DO
                END DO
            END DO
            
        END SUBROUTINE
